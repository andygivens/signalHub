import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import './tokens.css'

const ThemeCtx = createContext({ theme:'light', setTheme:()=>{} })
export const useTheme = () => useContext(ThemeCtx)

export function ThemeProvider({children, defaultTheme='light'}){
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || defaultTheme)
  useEffect(()=>{
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  },[theme])
  const value = useMemo(()=>({theme, setTheme}),[theme])
  return <ThemeCtx.Provider value={value}>{children}</ThemeCtx.Provider>
}