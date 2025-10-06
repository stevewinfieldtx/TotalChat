import React, { useEffect, useState } from 'react';

const backend = (import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000').replace(/\/?$/, '');

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
      .then(d => setCharacters((d.characters || []).map(c => ({ ...c, model: 'openrouter/auto' }))))
      .catch(() => setCharacters([]));
    setSelected([]);
  }, [activeCategory]);

  const toggle = (c) => {
    setSelected(prev => {
      const exists = prev.find(x => x.id === c.id);
      if (exists) return prev.filter(x => x.id !== c.id);
      if (prev.length >= 3) return prev; // cap at 3
      return [...prev, c];
    });
  };

  return (
    <div style={{ background: 'white', borderRadius: 12, padding: 16, boxShadow: '0 8px 20px rgba(0,0,0,0.08)' }}>
      <div style={{ display: 'flex', gap: 8, marginBottom: 12, flexWrap: 'wrap' }}>
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            style={{
              padding: '6px 12px',
              borderRadius: 999,
              border: activeCategory === cat ? '2px solid #4aa3ff' : '1px solid #e5e7eb',
              background: activeCategory === cat ? '#f0f7ff' : '#fff'
            }}
          >
            {cat}
          </button>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(240px,1fr))', gap: 12 }}>
        {characters.map(c => (
          <div key={c.id} style={{
            padding: 12,
            borderRadius: 12,
            border: selected.find(x => x.id === c.id) ? '2px solid #4aa3ff' : '1px solid #e5e7eb',
            cursor: 'pointer',
            display: 'flex',
            gap: 12,
            alignItems: 'center'
          }} onClick={() => toggle(c)}>
            <img src={c.images?.[0]} alt={c.name} width={40} height={40} style={{ borderRadius: '50%' }} />
            <div>
              <div style={{ fontWeight: 600 }}>{c.name}</div>
              <div style={{ opacity: 0.7 }}>{c.title}</div>
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 12 }}>
        <div style={{ opacity: 0.7 }}>Selected: {selected.map(s => s.name).join(', ') || 'none'}</div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={() => setSelected([])} className="back-button">Clear</button>
          <button onClick={() => onUseSelection(selected)} className="back-button">Use Selection</button>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;


