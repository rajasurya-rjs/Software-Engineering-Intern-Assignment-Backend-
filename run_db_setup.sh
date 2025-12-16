#!/bin/bash

echo "🔌 Connecting to NeonDB..."

DB_URL="postgresql://neondb_owner:npg_QXgCAz3mUOM9@ep-sweet-union-adde35pm-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

echo "📦 Running schema.sql..."
psql "$DB_URL" -f sql/schema.sql

if [ $? -ne 0 ]; then
  echo "❌ Schema execution failed"
  exit 1
fi

echo "🌱 Running seed.sql..."
psql "$DB_URL" -f sql/seed.sql

if [ $? -ne 0 ]; then
  echo "❌ Seed execution failed"
  exit 1
fi

echo "✅ Database setup completed successfully"
