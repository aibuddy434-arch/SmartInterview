import React from 'react';
import { clsx } from 'clsx';

const Input = React.forwardRef(({
  className = '',
  type = 'text',
  error = false,
  disabled = false,
  ...props
}, ref) => {
  const baseClasses = 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm transition-colors';
  const errorClasses = 'border-red-300 focus:border-red-500 focus:ring-red-500';
  const disabledClasses = 'bg-gray-50 cursor-not-allowed';
  
  const classes = clsx(
    baseClasses,
    error && errorClasses,
    disabled && disabledClasses,
    className
  );
  
  return (
    <input
      ref={ref}
      type={type}
      className={classes}
      disabled={disabled}
      {...props}
    />
  );
});

Input.displayName = 'Input';

export default Input;


