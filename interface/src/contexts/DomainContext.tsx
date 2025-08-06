/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState } from 'react'
import type { ReactNode } from 'react'

export type DomainContextType = {
  domains: string[]
  setDomains: (d: string[]) => void
  addDomain: (d: string) => void
  removeDomain: (d: string) => void
}

const DomainContext = createContext<DomainContextType | undefined>(undefined)

export function DomainProvider({
  children,
  initial = [],
}: {
  children: ReactNode
  initial?: string[]
}) {
  const [domains, setDomains] = useState<string[]>(initial)

  function addDomain(d: string) {
    setDomains((prev) => (prev.includes(d) ? prev : [...prev, d]))
  }

  function removeDomain(d: string) {
    setDomains((prev) => prev.filter((x) => x !== d))
  }

  return (
    <DomainContext.Provider value={{ domains, setDomains, addDomain, removeDomain }}>
      {children}
    </DomainContext.Provider>
  )
}

export function useDomains() {
  const ctx = useContext(DomainContext)
  if (!ctx) throw new Error('useDomains must be used within DomainProvider')
  return ctx
}
