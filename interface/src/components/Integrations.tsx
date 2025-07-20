export default function Integrations() {
  const items = ['S3', 'Postgres', 'n8n', 'Redis']
  return (
    <section data-observe>
      <div className="max-w-6xl mx-auto px-6 py-16 flex flex-wrap justify-center items-center space-x-4">
        {items.map((i) => (
          <span key={i} className="px-4 py-2 bg-gray-100 rounded text-sm font-medium">
            {i}
          </span>
        ))}
      </div>
    </section>
  )
}
