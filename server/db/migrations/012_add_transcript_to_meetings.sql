-- Migration: 012_add_transcript_to_meetings.sql
-- Add transcript column to meetings table for AI processing

ALTER TABLE meetings ADD COLUMN IF NOT EXISTS transcript TEXT;
