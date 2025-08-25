import React, { useEffect, useMemo, useRef, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import L from 'leaflet'
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

// Fix default icon paths for Leaflet when bundling
L.Icon.Default.mergeOptions({
	iconRetinaUrl: markerIcon2x,
	iconUrl: markerIcon,
	shadowUrl: markerShadow,
})

const DEFAULT_CENTER = [51.505, -0.09]
const LOCATION_ID = 'demo-square'

export default function App() {
	const [latest, setLatest] = useState({ count: 0, density: 0, timestamp: '' })
	const [alert, setAlert] = useState(false)
	const [history, setHistory] = useState([])
	const wsRef = useRef(null)

	useEffect(() => {
		const wsUrl = `ws://${window.location.hostname}:8000/ws/stream/${LOCATION_ID}`
		wsRef.current = new WebSocket(wsUrl)
		wsRef.current.onmessage = (event) => {
			const data = JSON.parse(event.data)
			setLatest({ count: data.count, density: data.density, timestamp: data.timestamp })
			setAlert(Boolean(data.alert))
			setHistory((prev) => [...prev.slice(-200), { time: new Date(data.timestamp).toLocaleTimeString(), count: data.count }])
		}
		wsRef.current.onerror = () => {
			console.error('WebSocket error')
		}
		return () => {
			try { wsRef.current && wsRef.current.close() } catch {}
		}
	}, [])

	const statusText = useMemo(() => alert ? 'Alert: Threshold exceeded' : 'Normal', [alert])

	return (
		<div className="app">
			<div className="left">
				<MapContainer center={DEFAULT_CENTER} zoom={13} style={{ height: '100%', width: '100%' }}>
					<TileLayer
						attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
						url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
					/>
					<Marker position={DEFAULT_CENTER}>
						<Popup>
							<strong>{LOCATION_ID}</strong><br />
							Count: {latest.count}<br />
							Density: {latest.density}
						</Popup>
					</Marker>
				</MapContainer>
			</div>
			<div className="right">
				<h2>Real-Time Crowd</h2>
				<div>Location: <code>{LOCATION_ID}</code></div>
				<div>Count: <strong>{latest.count}</strong></div>
				<div>Density: <strong>{latest.density}</strong></div>
				<div className={alert ? 'alert' : ''}>{statusText}</div>
				<h3>Count over time</h3>
				<div style={{ height: 240 }}>
					<ResponsiveContainer width="100%" height="100%">
						<LineChart data={history}>
							<XAxis dataKey="time" hide={true} />
							<YAxis allowDecimals={false} />
							<Tooltip />
							<Line type="monotone" dataKey="count" stroke="#3b82f6" dot={false} />
						</LineChart>
					</ResponsiveContainer>
				</div>
			</div>
		</div>
	)
}

