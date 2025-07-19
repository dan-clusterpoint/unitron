export default function Testimonials() {
  const items = [
    { name: 'Alex', quote: 'Unitron saved us hours of analysis.' },
    { name: 'Jamie', quote: 'Incredibly easy to integrate into our workflow.' },
    { name: 'Taylor', quote: 'A must-have tool for presales teams.' },
  ]
  return (
    <section className="bg-gray-50" data-observe>
      <div className="max-w-6xl mx-auto px-6 py-16 flex overflow-x-auto space-x-6">
        {items.map((t) => (
          <div key={t.name} className="flex-none w-80 bg-white p-6 rounded-lg shadow">
            <div className="flex items-center space-x-4 mb-2">
              <div className="w-10 h-10 rounded-full bg-gray-200" />
              <div className="font-medium">{t.name}</div>
            </div>
            <p className="text-sm text-gray-600">“{t.quote}”</p>
          </div>
        ))}
      </div>
    </section>
  )
}
