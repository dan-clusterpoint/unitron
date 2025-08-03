import crypto from 'crypto';
import OpenAI from 'openai';
import Redis from 'ioredis';
import { z } from 'zod';

export interface WebsiteContext {
  domains: string[];
  tech: string[];
  copy: string;
  jobs: string[];
}

export const GrowthTriggerSchema = z.object({
  title: z.string(),
  description: z.string(),
});
export type GrowthTrigger = z.infer<typeof GrowthTriggerSchema>;
const GrowthTriggerArray = z.array(GrowthTriggerSchema).max(3);

const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

let cacheHits = 0;
let cacheLookups = 0;

function sha256(text: string): string {
  return crypto.createHash('sha256').update(text).digest('hex');
}

function truncateTokens(text: string, limit = 1000): string {
  const tokens = text.split(/\s+/);
  if (tokens.length <= limit) return text;
  return tokens.slice(0, limit).join(' ');
}

async function fetchCopy(domain: string): Promise<string> {
  try {
    const res = await fetch(`https://${domain}`);
    const html = await res.text();
    return html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
  } catch {
    return '';
  }
}

async function fetchJobs(domain: string): Promise<string[]> {
  try {
    const res = await fetch(`https://${domain}/jobs`);
    if (!res.ok) throw new Error('no jobs');
    const html = await res.text();
    const text = html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
    return text ? [text] : [];
  } catch {
    return [];
  }
}

async function detectTech(_domain: string): Promise<string[]> {
  return [];
}

async function gatherContext(domains: string[]): Promise<string> {
  const primary = domains[0];
  const [copy, tech, jobs] = await Promise.all([
    fetchCopy(primary),
    detectTech(primary),
    fetchJobs(primary),
  ]);
  const context: WebsiteContext = { domains, tech, copy, jobs };
  return truncateTokens(JSON.stringify(context), 1000);
}

function buildPrompt(context: string): string {
  return [
    'You are the growth-trigger engine per spec §4.2.',
    'Given the following website context, list up to 3 growth triggers.',
    'Respond with a JSON array of {"title": string, "description": string}.',
    `Context: ${context}`,
  ].join('\n');
}

export async function growthTriggers(domains: string[]): Promise<GrowthTrigger[]> {
  const context = await gatherContext(domains);
  const cacheKey = sha256(context);
  cacheLookups += 1;
  const cached = await redis.get(cacheKey);
  if (cached) {
    cacheHits += 1;
    const hitRate = cacheHits / cacheLookups;
    console.log('growthTriggers cache hit', { cacheKey, hitRate });
    return JSON.parse(cached) as GrowthTrigger[];
  }

  const prompt = buildPrompt(context);

  let responseText = '';
  let usage = { prompt: 0, completion: 0, total: 0 };
  for (let attempt = 0; attempt < 3; attempt += 1) {
    try {
      const resp = await openai.chat.completions.create({
        model: 'gpt-4o',
        temperature: 0.2,
        messages: [{ role: 'user', content: prompt }],
      });
      responseText = resp.choices[0].message?.content ?? '';
      usage = {
        prompt: resp.usage?.prompt_tokens ?? 0,
        completion: resp.usage?.completion_tokens ?? 0,
        total: resp.usage?.total_tokens ?? 0,
      };
      break;
    } catch (err: any) {
      if (err.status === 429 && attempt < 2) {
        await new Promise((r) => setTimeout(r, 1000 * (attempt + 1)));
        continue;
      }
      console.error('growthTriggers openai error', err);
      return [];
    }
  }

  try {
    const parsed = GrowthTriggerArray.parse(JSON.parse(responseText));
    await redis.set(cacheKey, JSON.stringify(parsed), 'EX', 48 * 60 * 60);
    const cost = usage.prompt * 0.000005 + usage.completion * 0.000015;
    const hitRate = cacheHits / cacheLookups;
    console.log('growthTriggers cache miss', { cacheKey, usage, cost, hitRate });
    return parsed;
  } catch (err) {
    console.error('growthTriggers parse error', err);
    return [];
  }
}
