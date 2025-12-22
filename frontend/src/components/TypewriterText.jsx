// Typewriter effect component for streaming text
// During active streaming, shows text immediately. Typewriter effect only when complete.

import { useState, useEffect, useRef } from 'react';

export default function TypewriterText({ text = '', speed = 15, enabled = true, isStreaming = false, children }) {
  const [displayedText, setDisplayedText] = useState('');
  const indexRef = useRef(0);
  const timeoutRef = useRef(null);
  const lastTextRef = useRef('');

  useEffect(() => {
    if (!enabled || !text) {
      // If disabled or no text, show full text immediately
      setDisplayedText(text || '');
      indexRef.current = text ? text.length : 0;
      lastTextRef.current = text || '';
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      return;
    }

    // If text got shorter (new content started), reset
    if (text.length < lastTextRef.current.length) {
      setDisplayedText(text);
      indexRef.current = text.length;
      lastTextRef.current = text;
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      return;
    }

    // During active streaming: show text immediately (no typewriter effect)
    if (isStreaming) {
      setDisplayedText(text);
      indexRef.current = text.length;
      lastTextRef.current = text;
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      return;
    }

    // Typewriter effect only when NOT actively streaming (text is complete or paused)
    // If we're already displaying all the text, just update
    if (indexRef.current >= text.length) {
      setDisplayedText(text);
      lastTextRef.current = text;
      return;
    }

    // If new text arrived while we were typing, catch up quickly
    const charsBehind = text.length - indexRef.current;
    const shouldCatchUp = charsBehind > 50; // If more than 50 chars behind, catch up faster

    const typeNext = () => {
      if (indexRef.current < text.length) {
        // When catching up, type multiple characters at once for smooth experience
        const charsToAdd = shouldCatchUp ? Math.min(3, charsBehind) : 1;
        const newIndex = Math.min(indexRef.current + charsToAdd, text.length);
        const newText = text.substring(0, newIndex);
        setDisplayedText(newText);
        indexRef.current = newIndex;
        lastTextRef.current = newText;
        
        // Use variable speed - faster when catching up
        const currentChar = text[newIndex - 1];
        let charSpeed = shouldCatchUp ? speed * 0.2 : speed;
        
        if (currentChar === ' ' || currentChar === '\n') {
          charSpeed = charSpeed * 0.5; // Faster for spaces/newlines
        } else if (currentChar === '.' || currentChar === '!' || currentChar === '?') {
          charSpeed = charSpeed * 2; // Slower for sentence endings
        } else if (currentChar === ',' || currentChar === ';') {
          charSpeed = charSpeed * 1.5; // Slightly slower for commas
        }
        
        timeoutRef.current = setTimeout(typeNext, charSpeed);
      } else {
        // Reached end of current text
        lastTextRef.current = text;
        timeoutRef.current = null;
      }
    };

    // Start typing if we have new text to display and not already typing
    if (text.length > indexRef.current && !timeoutRef.current) {
      typeNext();
    }

    // Cleanup
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
    };
  }, [text, enabled, speed, isStreaming]);

  // Show cursor when actively streaming or when typewriter is still catching up
  const showCursor = (isStreaming && enabled) || (enabled && displayedText.length < text.length);

  // If children is a function, call it with displayedText
  if (typeof children === 'function') {
    return children(displayedText, showCursor);
  }

  // Otherwise, render the text directly
  return (
    <span>
      {displayedText}
      {showCursor && (
        <span className="inline-block w-0.5 h-4 bg-blue-600 ml-0.5 animate-pulse align-middle" />
      )}
    </span>
  );
}

