import { NextResponse } from 'next/server';

interface HealthCheckResponse {
  status: 'ok' | 'error';
  timestamp: string;
  version: string;
  uptime: number;
  environment: string;
}

export async function GET() {
  try {
    const uptime = process.uptime();
    
    const healthData: HealthCheckResponse = {
      status: 'ok',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      uptime: Math.floor(uptime),
      environment: process.env.NODE_ENV || 'development'
    };

    return NextResponse.json(healthData);
  } catch (error) {
    console.error('Health check failed:', error);
    
    const errorResponse: HealthCheckResponse = {
      status: 'error',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      uptime: 0,
      environment: process.env.NODE_ENV || 'development'
    };

    return NextResponse.json(errorResponse, { status: 500 });
  }
}
