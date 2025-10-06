import React, { useState } from 'react';
import { CheckCircle } from 'lucide-react';

const DEFAULT_CHARACTERS = [
  {
    id: 'socrates',
    name: 'Socrates',
    title: 'Philosopher',
    images: [
      'https://api.dicebear.com/7.x/avataaars/svg?seed=Socrates',
      'https://api.dicebear.com/7.x/avataaars/svg?seed=Socrates2',
      'https://api.dicebear.com/7.x/avataaars/svg?seed=Socrates3',
    ],
  },
  {
    id: 'cleopatra',
    name: 'Cleopatra',
    title: 'Queen of Egypt',
    images: [
      'https://api.dicebear.com/7.x/avataaars/svg?seed=Cleopatra',
      'https://api.dicebear.com/7.x/avataaars/svg?seed=Cleopatra2',
      'https://api.dicebear.com/7.x/avataaars/svg?seed=Cleopatra3',
    ],
  },
  {
    id: 'einstein',
    name: 'Albert Einstein',
    title: 'Physicist',
    images: [
      'https://api.dicebear.com/7.x/avataaars/svg?seed=Einstein',
      'https://api.dicebear.com/7.x/avataaars/svg?seed=Einstein2',
      'https://api.dicebear.com/7.x/avataaars/svg?seed=Einstein3',
    ],
  },
];

const CharacterSelector = ({ onSelectionComplete }) => {
  const [selectedIds, setSelectedIds] = useState([]);

  const toggle = (id) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id].slice(0, 3)
    );
  };

  const start = () => {
    const chosen = DEFAULT_CHARACTERS.filter((c) => selectedIds.includes(c.id));
    onSelectionComplete(chosen.length ? chosen : [DEFAULT_CHARACTERS[0]]);
  };

  return (
    <div style={{ maxWidth: 960, margin: '0 auto' }}>
      <h2 style={{ color: 'white', textAlign: 'center', marginBottom: '1rem' }}>
        Choose up to 3 characters
      </h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(260px,1fr))', gap: '1.25rem' }}>
        {DEFAULT_CHARACTERS.map((c) => (
          <button
            key={c.id}
            onClick={() => toggle(c.id)}
            style={{
              position: 'relative',
              padding: '1rem',
              borderRadius: 14,
              border: selectedIds.includes(c.id) ? '3px solid #4aa3ff' : '1px solid #e5e7eb',
              background: selectedIds.includes(c.id) ? 'linear-gradient(180deg,#ffffff 0%,#f0f7ff 100%)' : '#fff',
              boxShadow: selectedIds.includes(c.id)
                ? '0 8px 20px rgba(52,152,219,0.25)'
                : '0 4px 10px rgba(0,0,0,0.06)',
              transform: selectedIds.includes(c.id) ? 'translateY(-1px)' : 'none',
              textAlign: 'left',
              cursor: 'pointer',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <img src={c.images[0]} alt={c.name} width={48} height={48} style={{ borderRadius: '50%' }} />
              <div>
                <div style={{ fontWeight: 600 }}>{c.name}</div>
                <div style={{ opacity: 0.7 }}>{c.title}</div>
              </div>
            </div>
            {selectedIds.includes(c.id) && (
              <div style={{ position: 'absolute', top: 10, right: 10, color: '#2ecc71' }}>
                <CheckCircle size={22} />
              </div>
            )}
          </button>
        ))}
      </div>
      <div style={{ textAlign: 'center', marginTop: '1rem' }}>
        <button onClick={start} className="back-button">Start Chat</button>
      </div>
    </div>
  );
};

export default CharacterSelector;

