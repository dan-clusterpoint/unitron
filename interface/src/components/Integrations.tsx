export default function Integrations() {
  const items = ['S3', 'Postgres', 'n8n', 'Redis']
  return (
    <section data-observe>
      <div className="max-w-6xl mx-auto px-6 py-16 flex flex-wrap justify-center items-center">
        {items.map((i) => (
          <span key={i} className="tag-pill font-medium">
            {i}
          </span>
        ))}
      </div>
    </section>
  )
}
