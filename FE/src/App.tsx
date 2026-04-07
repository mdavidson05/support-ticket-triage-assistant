import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'

interface TriageResult {
  category: string
  urgency: string
  suggested_team: string
  sentiment: string
  summary: string
  recommended_next_action: string
  warnings: string[]
}

const SAMPLE_TICKETS: Record<string, string> = {
  'Login issue': "I can't log into my account. I've tried resetting my password twice but I never receive the reset email. This is blocking me from accessing my work.",
  'Billing problem': "I was charged twice for my subscription this month. My card ending in 4242 shows two identical charges of $49.99 on the 1st. Please refund the duplicate charge.",
  'Integration failure': "Our Zapier integration with your API stopped working yesterday. We're getting 401 Unauthorized errors on every request. Our API key hasn't changed and this was working fine last week.",
  'Feature request': "It would be really useful to have bulk export functionality. We manage hundreds of records and currently have to export them one by one which takes a very long time.",
}

const urgencyColour: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
  low: 'secondary',
  medium: 'outline',
  high: 'default',
  critical: 'destructive',
}

function App() {
  const [ticketText, setTicketText] = useState('')
  const [result, setResult] = useState<TriageResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async () => {
    if (!ticketText.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('http://localhost:8000/api/triage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticket_text: ticketText }),
      })

      if (!response.ok) throw new Error(`Server error: ${response.status}`)

      const data: TriageResult = await response.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-muted/40">

      {/* Header */}
      <header className="border-b bg-background px-8 py-4">
        <h1 className="text-lg font-semibold tracking-tight">Support ticket triage</h1>
      </header>

      <main className="max-w-2xl mx-auto px-8 py-10 space-y-6">

        {/* Sample tickets */}
        <div>
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3">
            Not sure what to ask? Try a sample ticket
          </p>
          <div className="flex flex-wrap gap-2">
            {Object.keys(SAMPLE_TICKETS).map((label) => (
              <Button
                key={label}
                variant="outline"
                size="sm"
                onClick={() => setTicketText(SAMPLE_TICKETS[label])}
              >
                {label}
              </Button>
            ))}
          </div>
        </div>

        <hr />

        {/* Input */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Ticket</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              placeholder="Write your support request here..."
              className="min-h-36 resize-none"
              value={ticketText}
              onChange={(e) => setTicketText(e.target.value)}
            />
            <Button
              onClick={handleSubmit}
              disabled={loading || !ticketText.trim()}
              className="w-full"
            >
              {loading ? 'Analysing...' : 'Triage ticket'}
            </Button>
          </CardContent>
        </Card>

        {/* Error */}
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Result */}
        {result && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium">Triage result</CardTitle>
                <div className="flex flex-wrap gap-1.5">
                  <Badge variant={urgencyColour[result.urgency] ?? 'outline'}>
                    {result.urgency}
                  </Badge>
                  <Badge variant="outline">{result.category}</Badge>
                  <Badge variant="outline">{result.sentiment}</Badge>
                  <Badge variant="secondary">{result.suggested_team}</Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">

              {result.warnings.length > 0 && (
                <Alert>
                  <AlertDescription>
                    <ul className="space-y-1">
                      {result.warnings.map((w, i) => (
                        <li key={i} className="text-sm">{w}</li>
                      ))}
                    </ul>
                  </AlertDescription>
                </Alert>
              )}

              <div className="divide-y text-sm">
                <div className="py-3 first:pt-0">
                  <p className="text-muted-foreground font-medium mb-1">Summary</p>
                  <p>{result.summary}</p>
                </div>
                <div className="py-3">
                  <p className="text-muted-foreground font-medium mb-1">Recommended action</p>
                  <p>{result.recommended_next_action}</p>
                </div>
                <div className="py-3 last:pb-0">
                  <p className="text-muted-foreground font-medium mb-1">Assigned team</p>
                  <p>{result.suggested_team}</p>
                </div>
              </div>

            </CardContent>
          </Card>
        )}

      </main>
    </div>
  )
}

export default App