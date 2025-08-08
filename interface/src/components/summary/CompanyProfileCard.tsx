import type { HTMLAttributes, SVGProps } from 'react'
import { EnvelopeIcon } from '@heroicons/react/24/solid'
import clsx from 'clsx'

function LinkedInIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="currentColor"
      aria-hidden="true"
      {...props}
    >
      <path d="M20.447 20.452h-3.554V14.75c0-1.359-.027-3.107-1.892-3.107-1.894 0-2.183 1.48-2.183 3.007v5.802H9.262V9h3.414v1.561h.049c.476-.9 1.637-1.849 3.367-1.849 3.601 0 4.267 2.37 4.267 5.455v6.285zM5.337 7.433c-1.144 0-2.07-.928-2.07-2.071 0-1.144.926-2.071 2.07-2.071 1.144 0 2.07.927 2.07 2.071 0 1.143-.926 2.071-2.07 2.071zm1.777 13.019H3.56V9h3.553v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.226.792 24 1.771 24h20.451C23.2 24 24 23.226 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
    </svg>
  )
}

function TwitterIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="currentColor"
      aria-hidden="true"
      {...props}
    >
      <path d="M23.954 4.569c-.885.388-1.83.654-2.825.775a4.93 4.93 0 0 0 2.163-2.724 9.86 9.86 0 0 1-3.127 1.195 4.922 4.922 0 0 0-8.384 4.482A13.97 13.97 0 0 1 1.671 3.149a4.822 4.822 0 0 0-.666 2.475 4.922 4.922 0 0 0 2.188 4.096 4.903 4.903 0 0 1-2.228-.616v.06a4.923 4.923 0 0 0 3.946 4.827 4.996 4.996 0 0 1-2.224.084 4.928 4.928 0 0 0 4.602 3.42 9.869 9.869 0 0 1-6.102 2.105c-.396 0-.79-.023-1.17-.068a13.951 13.951 0 0 0 7.548 2.212c9.055 0 14.01-7.498 14.01-14.002 0-.213 0-.425-.015-.637a10.014 10.014 0 0 0 2.457-2.548z" />
    </svg>
  )
}

export interface CompanyProfileProps extends HTMLAttributes<HTMLDivElement> {
  name: string
  website?: string
  industry?: string
  location?: string
  logoUrl?: string
  tagline?: string
  social?: {
    linkedin?: string
    twitter?: string
    email?: string
  }
}

export default function CompanyProfileCard({
  name,
  website,
  industry,
  location,
  logoUrl,
  tagline,
  social,
  className,
  ...props
}: CompanyProfileProps) {
  return (
    <div
      className={clsx(
        'flex items-center gap-4 p-4 border rounded bg-white',
        className,
      )}
      {...props}
    >
      {logoUrl && (
        <img
          src={logoUrl}
          alt={`${name} logo`}
          className="w-12 h-12 rounded object-cover"
        />
      )}
      <div className="text-sm">
        <div className="font-medium">{name}</div>
        {tagline && <div className="text-gray-600">{tagline}</div>}
        {industry && <div>{industry}</div>}
        {location && <div>{location}</div>}
        {website && (
          <a
            href={website}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 underline break-all"
          >
            {website}
          </a>
        )}
        {social && (
          <div className="flex gap-2 mt-1">
            {social.linkedin && (
              <a
                href={social.linkedin}
                target="_blank"
                rel="noopener noreferrer"
                aria-label="LinkedIn"
                className="text-gray-600 hover:text-gray-900"
              >
                <LinkedInIcon className="w-4 h-4" />
              </a>
            )}
            {social.twitter && (
              <a
                href={social.twitter}
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Twitter"
                className="text-gray-600 hover:text-gray-900"
              >
                <TwitterIcon className="w-4 h-4" />
              </a>
            )}
            {social.email && (
              <a
                href={
                  social.email.startsWith('mailto:')
                    ? social.email
                    : `mailto:${social.email}`
                }
                aria-label="Email"
                className="text-gray-600 hover:text-gray-900"
              >
                <EnvelopeIcon className="w-4 h-4" />
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
