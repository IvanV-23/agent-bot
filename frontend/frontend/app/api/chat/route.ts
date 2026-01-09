import { NextResponse } from 'next/server';
import axios from 'axios';

export async function POST(request: Request) {
  try {
    const body = await request.json();

    // Call your FastAPI backend from the server side
    const response = await axios.post('http://chatbot-api:8000/api/v1/chat', body, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    return NextResponse.json(response.data);
  } catch (error: any) {
    console.error("Proxy Error:", error.response?.data || error.message);
    return NextResponse.json(
      { error: "Failed to fetch from backend" },
      { status: error.response?.status || 500 }
    );
  }
}