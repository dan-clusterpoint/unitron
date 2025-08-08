import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table'
import { Progress } from '../ui/progress'
import type {
  AerisResponse,
  AerisBreakdownItem,
  AerisPeerItem,
  AerisVariantItem,
} from '../../types/aeris'

export default function AerisDashboard({ data }: { data: AerisResponse }) {
  const signals: AerisBreakdownItem[] = data.signal_breakdown ?? []
  const peers: AerisPeerItem[] = data.peers ?? []
  const variants: AerisVariantItem[] = data.variants ?? []
  const opportunities: string[] = data.opportunities ?? []
  const narratives: string[] = data.narratives ?? []

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>AERIS Score</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-4xl font-bold">{Math.round(data.core_score)}</div>
        </CardContent>
      </Card>

      {peers.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Peer Benchmark</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Peer</TableHead>
                  <TableHead className="text-right">Score</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {peers.map((p) => (
                  <TableRow key={p.name}>
                    <TableCell>{p.name}</TableCell>
                    <TableCell className="text-right">{p.score}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {signals.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Signals</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {signals.map((s) => (
              <div key={s.name}>
                <div className="flex justify-between text-sm mb-1">
                  <span>{s.name}</span>
                  <span>{s.score}</span>
                </div>
                <Progress value={s.score} max={100} />
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {variants.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Variants</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-end h-32 gap-2">
              {variants.map((v) => (
                <div key={v.name} className="flex-1">
                  <div
                    className="bg-primary w-full rounded-t"
                    style={{ height: `${v.score}%` }}
                  />
                  <div className="text-xs text-center mt-1">{v.name}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {opportunities.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Opportunities</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc pl-5 space-y-1 text-sm">
              {opportunities.map((o, i) => (
                <li key={i}>{o}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {narratives.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Narratives</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc pl-5 space-y-1 text-sm">
              {narratives.map((n, i) => (
                <li key={i}>{n}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
