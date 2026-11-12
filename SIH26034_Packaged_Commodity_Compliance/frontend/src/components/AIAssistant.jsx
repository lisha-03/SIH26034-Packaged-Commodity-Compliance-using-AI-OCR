import { useState, useRef, useEffect } from 'react'
import api, { errorMessage } from '../api'

// Floating AI assistant chat widget, powered by Gemini.
// New file — does not modify any existing component.
export default function AIAssistant() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Hi! I can help explain compliance results or how to use this tool. What do you need?' },
  ])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const scrollRef = useRef(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, open])

  const send = async () => {
    const text = input.trim()
    if (!text || sending) return
    setError('')
    setInput('')
    const nextMessages = [...messages, { role: 'user', text }]
    setMessages(nextMessages)
    setSending(true)
    try {
      const history = nextMessages.slice(0, -1).map(m => ({ role: m.role, text: m.text }))
      const res = await api.post('/ai/chat', { message: text, history })
      setMessages(m => [...m, { role: 'assistant', text: res.data.reply }])
    } catch (err) {
      setError(errorMessage(err, 'Could not reach the AI assistant.'))
    } finally {
      setSending(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  return (
    <>
      {open && (
        <div className="fixed bottom-24 right-6 w-80 max-h-[28rem] bg-white rounded-xl shadow-2xl border border-gray-200 flex flex-col z-50">
          <div className="px-4 py-3 bg-navy-950 text-white rounded-t-xl flex items-center justify-between">
            <span className="text-sm font-semibold">AI Assistant</span>
            <button onClick={() => setOpen(false)} className="text-white/70 hover:text-white text-sm">✕</button>
          </div>
          <div ref={scrollRef} className="flex-1 overflow-y-auto px-3 py-3 space-y-2 text-sm">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`rounded-lg px-3 py-2 max-w-[85%] whitespace-pre-wrap ${
                  m.role === 'user' ? 'bg-blue-600 text-white ml-auto' : 'bg-gray-100 text-gray-800'
                }`}
              >
                {m.text}
              </div>
            ))}
            {sending && <div className="text-xs text-gray-400 px-1">Thinking…</div>}
            {error && <div className="text-xs text-red-600 px-1">{error}</div>}
          </div>
          <div className="border-t border-gray-200 p-2 flex gap-2">
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              placeholder="Ask something…"
              className="flex-1 resize-none rounded-lg border border-gray-300 px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={send}
              disabled={sending}
              className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm rounded-lg px-3"
            >
              Send
            </button>
          </div>
        </div>
      )}
      <button
        onClick={() => setOpen(o => !o)}
        className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-navy-950 hover:bg-navy-800 text-white text-2xl shadow-xl flex items-center justify-center z-50"
        title="AI Assistant"
      >
        💬
      </button>
    </>
  )
}
