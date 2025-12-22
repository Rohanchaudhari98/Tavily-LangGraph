// Typewriter effect component for streaming text
// Similar to ChatGPT/Claude's streaming display
// Works with ReactMarkdown by rendering children with the displayed text

import { useState, useEffect, useRef } from 'react';

export default function TypewriterText({ text = '', speed = 15, enabled = true, children }) {
  const [displayedText, setDisplayedText] = useState('');
  const textRef = useRef(text);
  const indexRef = useRef(0);
  const timeoutRef = useRef(null);
  const lastTextLengthRef = useRef(0);

  useEffect(() => {
    // Update the ref when text changes
    textRef.current = text;
  }, [text]);

  useEffect(() => {
    if (!enabled) {
      // If disabled, show full text immediately
      setDisplayedText(text);
      lastTextLengthRef.current = text.length;
      indexRef.current = text.length;
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      return;
    }

    // If text got shorter (new content started), reset
    if (text.length < lastTextLengthRef.current) {
      setDisplayedText(text);
      indexRef.current = text.length;
      lastTextLengthRef.current = text.length;
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      return;
    }

    // If we're already displaying all the text, no need to animate
    if (indexRef.current >= text.length) {
      lastTextLengthRef.current = text.length;
      return;
    }

    // Don't restart if we're already typing
    if (timeoutRef.current) {
      return;
    }

    const typeNext = () => {
      if (indexRef.current < text.length) {
        const newText = text.substring(0, indexRef.current + 1);
        setDisplayedText(newText);
        indexRef.current += 1;
        lastTextLengthRef.current = newText.length;
        
        // Use variable speed - faster for spaces, slower for punctuation
        const currentChar = text[indexRef.current - 1];
        let charSpeed = speed;
        if (currentChar === ' ' || currentChar === '\n') {
          charSpeed = speed * 0.5; // Faster for spaces/newlines
        } else if (currentChar === '.' || currentChar === '!' || currentChar === '?') {
          charSpeed = speed * 2; // Slower for sentence endings
        } else if (currentChar === ',' || currentChar === ';') {
          charSpeed = speed * 1.5; // Slightly slower for commas
        }
        
        timeoutRef.current = setTimeout(typeNext, charSpeed);
      } else {
        // Reached end of current text, but more might come
        lastTextLengthRef.current = text.length;
        timeoutRef.current = null;
      }
    };

    // Start typing immediately if we have new text to display
    if (text.length > indexRef.current) {
      typeNext();
    }

    // Cleanup
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
    };
  }, [text, enabled, speed]);

  // Show cursor when streaming
  const isStreaming = enabled && displayedText.length < text.length;

  // If children is a function, call it with displayedText
  if (typeof children === 'function') {
    return children(displayedText, isStreaming);
  }

  // Otherwise, render the text directly
  return (
    <span>
      {displayedText}
      {isStreaming && (
        <span className="inline-block w-0.5 h-4 bg-blue-600 ml-0.5 animate-pulse align-middle" />
      )}
    </span>
  );
}

