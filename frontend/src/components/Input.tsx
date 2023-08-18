import React from 'react';
import { InputProps } from '@/types';

const Input: React.FC<InputProps> = ({ id, onChange, value, label, type, error }): JSX.Element => {
  return (
    <div className="relative">
      <input
        onChange={onChange}
        value={value}
        id={id}
        type={type}
        className="
        block
        rounded-md
        pl-2
        pr-6
        pt-6
        pb-1
        w-full
        text-md
        font-inter
        text-[#6f7479]
        appearance-none
        focus:outline-none
        focus:ring-0
        peer
      "
        placeholder=" "
      />
      <label
        htmlFor={id}
        className="
        absolute
        cursor-text
        text-md
        text-zinc-400
        duration-150
        transform
        -translate-y-3
        scale-75
        top-4
        z-10
        origin-[0]
        left-2
        peer-placeholder-shown:scale-100
        peer-placeholder-shown:translate-y-0
        peer-focus:scale-75
        peer-focus:-translate-y-3
      "
      >
        {label}
      </label>
      <div className="line peer-focus:border-primary"></div>
      {error && <p className="text-warn text-xs mt-2">{error}</p>}
    </div>
  );
};

export default Input;
