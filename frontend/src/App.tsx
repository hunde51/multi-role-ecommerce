import { useEffect, useState } from 'react'
import { getBackendMessage } from './service/api'

export default function App() {
  const [message, setMessage] = useState('Loading backend...')

  useEffect(() => {
    const loadMessage = async () => {
      const backendMessage = await getBackendMessage()
      setMessage(backendMessage)
    }

    void loadMessage()
  }, [])

  return (
    <div>
      <h1>Frontend Connected</h1>
      <p>{message}</p>
    </div>
  )
}
