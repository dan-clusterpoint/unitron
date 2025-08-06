export default function Testimonials() {
  const items = [
    { name: 'Alex', quote: 'Unitron saved us hours of analysis.' },
    { name: 'Jamie', quote: 'Incredibly easy to integrate into our workflow.' },
    { name: 'Taylor', quote: 'A must-have tool for presales teams.' },
  ]
  return (
    <section className="bg-gray-50" data-observe>
      <div className="max-w-6xl mx-auto px-6 py-16 flex overflow-x-auto space-x-6 md:justify-center">
        {items.map((t) => {
          const initials = t.name
            .split(/\s+/)
            .map((n) => n[0])
            .join('')
            .toUpperCase()

          return (
            <div key={t.name} className="testimonial-card flex-none w-80">
              <div className="flex items-center space-x-4 mb-2">
                <div className="avatar avatar-initials">{initials}</div>
                <div className="font-medium">{t.name}</div>
              </div>
              <p className="text-sm text-gray-600">“{t.quote}”</p>
            </div>
          )
        })}
      </div>
    </section>
  )
}
