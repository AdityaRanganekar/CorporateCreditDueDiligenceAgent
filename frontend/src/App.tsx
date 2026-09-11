import { useState } from 'react'
import { fetchEventSource } from '@microsoft/fetch-event-source'
import ReactMarkdown from 'react-markdown'
// @ts-ignore
import html2pdf from 'html2pdf.js'

interface Message {
  id: string
  role: 'user' | 'agent' | 'system'
  content: string
}

interface PendingReview {
  thread_id: string
  pending_node: string
}

// The signature Gemini sparkle icon
const SparkleIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ flexShrink: 0, marginTop: '4px' }}>
    <path d="M16 8C16 8 17 5 20 5C17 5 16 2 16 2C16 2 15 5 12 5C15 5 16 8 16 8ZM8 22C8 22 9.5 14.5 15 13C9.5 11.5 8 4 8 4C8 4 6.5 11.5 1 13C6.5 14.5 8 22 8 22Z" fill="#a8c7fa"/>
  </svg>
)

export default function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [pendingReview, setPendingReview] = useState<PendingReview | null>(null)

  const handleSend = async () => {
    if (!inputText.trim()) return

    const threadId = `thread_${Date.now()}`
    setMessages(prev => [...prev, { id: `msg_${Date.now()}`, role: 'user', content: inputText }])
    setInputText('')
    setIsStreaming(true)
    setPendingReview(null)

    await fetchEventSource('http://localhost:8080/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ raw_document: inputText, thread_id: threadId }),
      async onmessage(ev) {
        try {
          if (!ev.data) return 
          const data = JSON.parse(ev.data)
          
          if (data.status === 'interrupted') {
            setPendingReview({ thread_id: threadId, pending_node: data.pending_node })
            setIsStreaming(false)
          } else if (data.status === 'completed') {
            setMessages(prev => [...prev, { id: `msg_${Date.now()}`, role: 'agent', content: data.memo }])
            setIsStreaming(false)
          }
        } catch (err) {
          console.error("Parse Error:", ev.data)
        }
      },
      onerror(err) {
        console.error('Stream Error:', err)
        setIsStreaming(false)
        throw err 
      }
    })
  }

  const handleApprove = async (approve: boolean) => {
    if (!pendingReview) return
    setIsStreaming(true)
    
    try {
      const response = await fetch('http://localhost:8080/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ thread_id: pendingReview.thread_id, approve })
      })
      const data = await response.json()
      
      if (data.status === 'resumed_and_completed') {
        setMessages(prev => [...prev, { id: `msg_${Date.now()}`, role: 'agent', content: data.final_memo }])
      } else {
        setMessages(prev => [...prev, { id: `msg_${Date.now()}`, role: 'system', content: 'Underwriting process aborted by human oversight.' }])
      }
    } catch (err) {
      console.error(err)
    } finally {
      setPendingReview(null)
      setIsStreaming(false)
    }
  }

  const downloadPDF = (elementId: string) => {
    const element = document.getElementById(elementId)
    if (!element) return

    const clone = element.cloneNode(true) as HTMLElement
    clone.classList.add('pdf-export-mode')
    
    const d = new Date()
    const timestamp = `${d.getFullYear()}_${String(d.getMonth()+1).padStart(2,'0')}_${String(d.getDate()).padStart(2,'0')}_${String(d.getHours()).padStart(2,'0')}_${String(d.getMinutes()).padStart(2,'0')}`
    
    const opt = {
      margin: 0.5,
      filename: `credit_memo_${timestamp}.pdf`,
      image: { type: 'jpeg' as 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, windowWidth: 800 },
      jsPDF: { unit: 'in' as 'in', format: 'letter', orientation: 'portrait' as 'portrait' }
    }

    html2pdf().set(opt).from(clone).save()
  }

  const geminiGradient = {
    background: 'linear-gradient(90deg, #4285F4, #9B72CB, #D96570)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    display: 'inline-block'
  }

  return (
    <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', position: 'relative' }}>
      
      {/* Header */}
      <header style={{ padding: '20px 24px', position: 'absolute', top: 0, left: 0, right: 0, zIndex: 10 }}>
        <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 500, ...geminiGradient }}>
          Credit Due Diligence Agent
        </h2>
      </header>
      
      {/* Chat Area */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '80px 20px 120px 20px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ width: '100%', maxWidth: '800px', display: 'flex', flexDirection: 'column', gap: '32px' }}>
          
          {messages.length === 0 && (
            <div style={{ margin: 'auto', marginTop: '8vh', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px', width: '100%' }}>
              <SparkleIcon />
              <h1 style={{ fontSize: '36px', fontWeight: 500, margin: '8px 0 0 0', ...geminiGradient }}>
                Hello, Underwriter.
              </h1>
              <p style={{ color: '#c4c7c5', fontSize: '18px', margin: 0, textAlign: 'center', maxWidth: '550px' }}>
                Paste raw commercial loan application details below to begin automated feature extraction and risk scoring.
              </p>
              
              <div style={{ width: '100%', maxWidth: '600px', marginTop: '32px' }}>
                <h3 style={{ margin: '0 0 12px 16px', fontSize: '14px', color: '#a8c7fa', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Supported Data Points</h3>
                <ul style={{ margin: '0 0 24px 0', paddingLeft: '32px', color: '#c4c7c5', fontSize: '15px', lineHeight: 1.8 }}>
                  <li>Loan Amount, Duration, Interest Rate</li>
                  <li>Monthly Payment, Income, Debt-to-Income (DTI)</li>
                  <li>History of bankruptcies or defaults</li>
                </ul>
                
                <div 
                  onClick={() => setInputText("The applicant is applying for a $50,000 commercial loan over a 24-month term at a 25% interest rate, with an expected monthly payment of $2,200. Their stated income is $15,000 resulting in an 85% DTI, and their credit file shows 4 previous bankruptcies.")}
                  style={{ padding: '20px', backgroundColor: '#1e1f20', borderRadius: '24px', cursor: 'pointer', border: '1px solid transparent', transition: 'all 0.2s ease', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}
                  onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#282a2c'}
                  onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#1e1f20'}
                >
                  <span style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#a8c7fa', fontSize: '13px', fontWeight: 500, marginBottom: '8px' }}>
                    💡 Sample High-Risk Profile
                  </span>
                  <span style={{ color: '#e3e3e3', fontSize: '15px', lineHeight: 1.5 }}>
                    "The applicant is applying for a $50,000 commercial loan over a 24-month term at a 25% interest rate, with an expected monthly payment of $2,200. Their stated income is $15,000 resulting in an 85% DTI, and their credit file shows 4 previous bankruptcies."
                  </span>
                </div>
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <div key={msg.id} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start', width: '100%', gap: '16px' }}>
              
              {msg.role === 'agent' && <SparkleIcon />}

              {msg.role === 'user' && (
                <div style={{ backgroundColor: '#282a2c', padding: '14px 24px', borderRadius: '28px 28px 4px 28px', color: '#e3e3e3', maxWidth: '70%', lineHeight: 1.5, fontSize: '16px' }}>
                  {msg.content}
                </div>
              )}

              {msg.role === 'system' && (
                <div style={{ backgroundColor: '#311313', color: '#f2b8b5', padding: '12px 20px', borderRadius: '12px', width: '100%', border: '1px solid #8c1d18' }}>
                  {msg.content}
                </div>
              )}

              {msg.role === 'agent' && (
                <div style={{ width: '100%', paddingTop: '4px' }}>
                  <div id={msg.id} className="agent-markdown" style={{ paddingBottom: '16px' }}>
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                  <button 
                    onClick={() => downloadPDF(msg.id)}
                    style={{ background: 'transparent', border: '1px solid #444746', color: '#c4c7c5', padding: '8px 16px', borderRadius: '20px', cursor: 'pointer', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px', marginTop: '12px', fontWeight: 500, transition: 'background-color 0.2s' }}
                    onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#282a2c'}
                    onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                    Export as PDF
                  </button>
                </div>
              )}
            </div>
          ))}
          
          {isStreaming && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', color: '#a8c7fa', fontWeight: 500 }}>
              <SparkleIcon />
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', paddingTop: '4px' }}>
                <div className="spinner" style={{ width: '14px', height: '14px', border: '2px solid #a8c7fa', borderTop: '2px solid transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
                <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
                Thinking...
              </div>
            </div>
          )}
          
          {pendingReview && (
            <div style={{ border: '1px solid #8c1d18', padding: '24px', borderRadius: '24px', backgroundColor: '#311313', color: '#f2b8b5', width: '100%', boxSizing: 'border-box', marginLeft: '40px' }}>
              <strong style={{ fontSize: '18px', display: 'block', marginBottom: '8px', fontWeight: 500 }}>Action Required: High-Risk Profile Detected</strong>
              <p style={{ margin: 0, marginBottom: '20px', lineHeight: 1.5, color: '#e3e3e3' }}>The ML model flagged this application. Do you authorize memo generation?</p>
              <div style={{ display: 'flex', gap: '12px' }}>
                <button onClick={() => handleApprove(true)} style={{ padding: '10px 24px', backgroundColor: '#f2b8b5', color: '#311313', border: 'none', borderRadius: '24px', cursor: 'pointer', fontWeight: 600, fontSize: '14px' }}>Approve Override</button>
                <button onClick={() => handleApprove(false)} style={{ padding: '10px 24px', backgroundColor: 'transparent', color: '#f2b8b5', border: '1px solid #f2b8b5', borderRadius: '24px', cursor: 'pointer', fontWeight: 600, fontSize: '14px' }}>Reject</button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, padding: '24px', display: 'flex', justifyContent: 'center', background: 'linear-gradient(to top, #131314 80%, transparent)' }}>
        <div style={{ width: '100%', maxWidth: '800px', display: 'flex', background: '#1e1f20', borderRadius: '32px', padding: '8px 8px 8px 24px', gap: '12px', alignItems: 'center', boxShadow: '0 4px 12px rgba(0,0,0,0.2)' }}>
          <input 
            type="text" 
            value={inputText} 
            onChange={e => setInputText(e.target.value)} 
            onKeyDown={e => e.key === 'Enter' && handleSend()}
            placeholder="Paste raw loan application details..." 
            style={{ flex: 1, border: 'none', backgroundColor: 'transparent', color: 'white', outline: 'none', fontSize: '16px', fontFamily: 'inherit' }}
            disabled={isStreaming || !!pendingReview}
          />
          <button 
            onClick={handleSend} 
            disabled={isStreaming || !!pendingReview || !inputText.trim()}
            style={{ padding: '12px', backgroundColor: inputText.trim() && !isStreaming && !pendingReview ? '#e3e3e3' : '#444746', color: inputText.trim() && !isStreaming && !pendingReview ? '#131314' : '#131314', border: 'none', borderRadius: '50%', cursor: inputText.trim() && !isStreaming && !pendingReview ? 'pointer' : 'default', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'background-color 0.2s' }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
          </button>
        </div>
      </div>
    </div>
  )
}