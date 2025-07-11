// File: frontend/src/components/common/Loading.tsx

import React from 'react'

const Loading: React.FC = () => {
  return (
    <div className="flex items-center justify-center h-full p-4">
      <div className="text-center text-gray-300 animate-pulse">
        <div className="text-2xl font-semibold">Carregando...</div>
        <div className="mt-2 text-sm text-gray-400">Aguarde um instante</div>
      </div>
    </div>
  )
}

export default Loading;
