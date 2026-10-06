module.exports = {
  content: ['../../index.html'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        display: ['"Bricolage Grotesque"', 'ui-sans-serif', 'system-ui', 'Segoe UI', 'sans-serif'],
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'Segoe UI', 'Helvetica Neue', 'Arial', 'sans-serif']
      },
      colors: {
        ink:   { 50:'#f6f7fb', 100:'#eceef7', 700:'#2b2f45', 800:'#1c2033', 900:'#12152a', 950:'#0a0c1a' },
        brand: { 50:'#eef2ff',100:'#e0e7ff',200:'#c7d2fe',300:'#a5b4fc',400:'#818cf8',
                 500:'#6366f1',600:'#4f46e5',700:'#4338ca',800:'#3730a3',900:'#312e81' }
      },
      boxShadow: {
        pop:  '0 10px 30px -10px rgba(79,70,229,.35)',
        lift: '0 18px 40px -14px rgba(15,23,42,.30)'
      },
      keyframes: {
        floaty:  { '0%,100%':{transform:'translateY(0)'}, '50%':{transform:'translateY(-14px)'} },
        drift:   { '0%,100%':{transform:'translate(0,0) scale(1)'}, '50%':{transform:'translate(24px,-16px) scale(1.06)'} },
        shimmer: { '0%':{backgroundPosition:'0% 50%'}, '50%':{backgroundPosition:'100% 50%'}, '100%':{backgroundPosition:'0% 50%'} },
        pulseRing:{ '0%':{transform:'scale(.9)',opacity:'.7'}, '70%':{transform:'scale(1.35)',opacity:'0'}, '100%':{opacity:'0'} },
        popIn:   { from:{opacity:'0',transform:'translateY(14px) scale(.98)'}, to:{opacity:'1',transform:'none'} }
      },
      animation: {
        floaty:'floaty 7s ease-in-out infinite',
        drift:'drift 14s ease-in-out infinite',
        shimmer:'shimmer 9s ease infinite',
        pulseRing:'pulseRing 2.4s cubic-bezier(.24,.86,.5,1) infinite',
        popIn:'popIn .28s cubic-bezier(.2,.8,.2,1) both'
      }
    }
  }
}
