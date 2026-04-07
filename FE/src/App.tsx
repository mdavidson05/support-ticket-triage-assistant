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
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-2xl mx-auto space-y-6">

        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Support ticket triage</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Paste a support ticket below and get an instant AI triage analysis.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Ticket</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              placeholder="Paste support ticket text here..."
              className="min-h-32 resize-none"
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

        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {result && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Triage result</CardTitle>
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

              <div className="flex flex-wrap gap-2">
                <Badge variant={urgencyColour[result.urgency] ?? 'outline'}>
                  {result.urgency}
                </Badge>
                <Badge variant="outline">{result.category}</Badge>
                <Badge variant="outline">{result.sentiment}</Badge>
                <Badge variant="secondary">{result.suggested_team}</Badge>
              </div>

              <div className="space-y-3 text-sm">
                <div>
                  <p className="text-muted-foreground font-medium mb-0.5">Summary</p>
                  <p>{result.summary}</p>
                </div>
                <div>
                  <p className="text-muted-foreground font-medium mb-0.5">Recommended action</p>
                  <p>{result.recommended_next_action}</p>
                </div>
                <div>
                  <p className="text-muted-foreground font-medium mb-0.5">Assigned team</p>
                  <p>{result.suggested_team}</p>
                </div>
              </div>

            </CardContent>
          </Card>
        )}

      </div>
    </div>
  )
}

export default App