import React, { useEffect, useState } from 'react';

// Use VITE_BACKEND_URL if set, otherwise use same origin (for Railway) or localhost for dev
const getBackendUrl = () => {
  const envUrl = import.meta.env.VITE_BACKEND_URL;
  if (envUrl) return envUrl.replace(/\/?$/, '');
  // In production (Railway), backend serves on same origin
  if (import.meta.env.PROD) return window.location.origin;
  // In development, use localhost
  return 'http://localhost:8000';
};

const backend = getBackendUrl();

const AdminPanel = ({ onUseSelection }) => {
  const [categories, setCategories] = useState([]);
  const [activeCategory, setActiveCategory] = useState('Education');
  const [characters, setCharacters] = useState([]);
  const [selected, setSelected] = useState([]);

  useEffect(() => {
    fetch(`${backend}/api/characters/categories`)
      .then(r => r.json())
      .then(d => setCategories(d.categories || []))
      .catch(() => setCategories([]));
  }, []);

  useEffect(() => {
    if (!activeCategory) return;
    fetch(`${backend}/api/characters/${activeCategory}`)
      .then(r => r.json())
      .then(async d => {
        // Fetch full character data to get LLM field
        const charactersWithModels = await Promise.all((d.characters || []).map(async c => {
          try {
            const fullData = await fetch(`${backend}/api/characters/${activeCategory}/${c.id}`).then(r => r.json());
            // Look for llm field in various possible locations, default to x-ai/grok-4-fast
            const llm = fullData.llm || fullData.model || fullData.metadata?.llm || 'x-ai/grok-4-fast';
            return { ...c, model: llm };
          } catch (error) {
            return { ...c, model: 'x-ai/grok-4-fast' };
          }
        }));
        setCharacters(charactersWithModels);
      })
      .catch(() => setCharacters([]));
    setSelected([]);
  }, [activeCategory]);

  const toggle = (c) => {
    setSelected(prev => {
      const exists = prev.find(x => x.id === c.id);
      if (exists) return prev.filter(x => x.id !== c.id);
      if (prev.length >= 2) return prev; // cap at 2
      return [...prev, c];
    });
  };

  return (
    <div style={{
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      borderRadius: 20,
      padding: 32,
      boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
      color: 'white'
    }}>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ margin: 0, fontSize: 28, fontWeight: 700, marginBottom: 8 }}>
          🎭 Character Selection
        </h2>
        <p style={{ margin: 0, opacity: 0.9, fontSize: 14 }}>
          Choose a folder, then select 1-2 characters to chat with
        </p>
      </div>

      <div style={{
        display: 'flex',
        gap: 12,
        marginBottom: 24,
        flexWrap: 'wrap'
      }}>
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            style={{
              padding: '12px 24px',
              borderRadius: 12,
              border: 'none',
              background: activeCategory === cat
                ? 'rgba(255,255,255,0.95)'
                : 'rgba(255,255,255,0.2)',
              color: activeCategory === cat ? '#667eea' : 'white',
              fontWeight: 600,
              fontSize: 14,
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              backdropFilter: 'blur(10px)',
              boxShadow: activeCategory === cat
                ? '0 8px 16px rgba(0,0,0,0.2)'
                : 'none'
            }}
          >
            📁 {cat.replace(/_/g, ' ')}
          </button>
        ))}
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: 16,
        marginBottom: 24
      }}>
        {characters.map(c => {
          const isSelected = selected.find(x => x.id === c.id);
          return (
            <div
              key={c.id}
              onClick={() => toggle(c)}
              style={{
                padding: 20,
                borderRadius: 16,
                background: isSelected
                  ? 'rgba(255,255,255,0.95)'
                  : 'rgba(255,255,255,0.15)',
                border: isSelected
                  ? '3px solid #fbbf24'
                  : '2px solid rgba(255,255,255,0.3)',
                cursor: 'pointer',
                display: 'flex',
                gap: 16,
                alignItems: 'center',
                transition: 'all 0.3s ease',
                backdropFilter: 'blur(10px)',
                transform: isSelected ? 'scale(1.02)' : 'scale(1)',
                boxShadow: isSelected
                  ? '0 12px 24px rgba(0,0,0,0.3)'
                  : '0 4px 8px rgba(0,0,0,0.1)'
              }}
            >
              <img
                src={c.images?.[0]}
                alt={c.name}
                width={60}
                height={60}
                style={{
                  borderRadius: '50%',
                  border: '3px solid rgba(255,255,255,0.5)',
                  boxShadow: '0 4px 8px rgba(0,0,0,0.2)'
                }}
              />
              <div style={{ flex: 1 }}>
                <div style={{
                  fontWeight: 700,
                  fontSize: 16,
                  marginBottom: 4,
                  color: isSelected ? '#667eea' : 'white'
                }}>
                  {c.name}
                </div>
                <div style={{
                  fontSize: 13,
                  opacity: 0.8,
                  color: isSelected ? '#764ba2' : 'rgba(255,255,255,0.8)',
                  marginBottom: 6
                }}>
                  {c.title}
                </div>
                <div style={{
                  fontSize: 11,
                  padding: '4px 8px',
                  borderRadius: 6,
                  background: isSelected ? '#667eea' : 'rgba(255,255,255,0.2)',
                  color: 'white',
                  display: 'inline-block',
                  fontWeight: 600
                }}>
                  🤖 {c.model || 'x-ai/grok-4-fast'}
                </div>
              </div>
              {isSelected && (
                <div style={{
                  fontSize: 24,
                  color: '#fbbf24'
                }}>
                  ✓
                </div>
              )}
            </div>
          );
        })}
      </div>

      {characters.length === 0 && activeCategory && (
        <div style={{
          padding: 40,
          textAlign: 'center',
          background: 'rgba(255,255,255,0.1)',
          borderRadius: 12,
          marginBottom: 24
        }}>
          <div style={{ fontSize: 48, marginBottom: 12 }}>📭</div>
          <div style={{ fontSize: 16, opacity: 0.9 }}>
            No characters found in {activeCategory}
          </div>
        </div>
      )}

      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: 20,
        background: 'rgba(0,0,0,0.2)',
        borderRadius: 12,
        backdropFilter: 'blur(10px)'
      }}>
        <div style={{
          fontSize: 14,
          fontWeight: 600
        }}>
          {selected.length === 0 && '👉 Select 1-2 characters to continue'}
          {selected.length === 1 && `✨ ${selected[0].name} selected (you can add 1 more)`}
          {selected.length === 2 && `🎉 Ready! ${selected.map(s => s.name).join(' & ')}`}
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          {selected.length > 0 && (
            <button
              onClick={() => setSelected([])}
              style={{
                padding: '12px 24px',
                borderRadius: 10,
                border: 'none',
                background: 'rgba(255,255,255,0.2)',
                color: 'white',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                fontSize: 14
              }}
            >
              Clear
            </button>
          )}
          <button
            onClick={() => onUseSelection(selected)}
            disabled={selected.length === 0}
            style={{
              padding: '12px 32px',
              borderRadius: 10,
              border: 'none',
              background: selected.length > 0
                ? 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)'
                : 'rgba(255,255,255,0.1)',
              color: 'white',
              fontWeight: 700,
              cursor: selected.length > 0 ? 'pointer' : 'not-allowed',
              transition: 'all 0.3s ease',
              fontSize: 14,
              boxShadow: selected.length > 0
                ? '0 8px 16px rgba(0,0,0,0.3)'
                : 'none',
              opacity: selected.length > 0 ? 1 : 0.5
            }}
          >
            Start Chat 💬
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;


