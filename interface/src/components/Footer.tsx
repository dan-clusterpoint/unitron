export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300" id="contact">
      <div className="max-w-6xl mx-auto px-4 py-16">
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          <div>
            <h3 className="font-semibold mb-2">Site</h3>
            <ul className="space-y-1 text-sm">
              <li><a href="#home" className="hover:text-white">Home</a></li>
              <li><a href="/docs" className="hover:text-white">Docs</a></li>
              <li><a href="https://github.com" className="hover:text-white">GitHub</a></li>
              <li><a href="#contact" className="hover:text-white">Contact</a></li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Newsletter</h3>
            <form className="flex space-x-2">
              <input
                type="email"
                placeholder="Your email"
                aria-label="email"
                className="flex-1 p-2 rounded text-gray-900"
              />
              <button type="submit" className="px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark transition">
                Sign Up
              </button>
            </form>
          </div>
        </div>
        <div className="text-center text-sm mt-8 border-t border-gray-700 pt-4">
          © {new Date().getFullYear()} Unitron · Developed with ❤️ by Unitron
        </div>
      </div>
    </footer>
  )
}
