import type { HTMLAttributes } from 'react'
import clsx from 'clsx'

export interface CompanyProfileProps extends HTMLAttributes<HTMLDivElement> {
  name: string
  website?: string
  industry?: string
  location?: string
  logoUrl?: string
}

export default function CompanyProfileCard({
  name,
  website,
  industry,
  location,
  logoUrl,
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
      </div>
    </div>
  )
}
