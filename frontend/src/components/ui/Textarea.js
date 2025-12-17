import React from 'react';
import { clsx } from 'clsx';

const Textarea = React.forwardRef(({
  className = '',
  rows = 4,
  error = false,
  disabled = false,
  ...props
}, ref) => {
  const baseClasses = 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm transition-colors resize-vertical';
  const errorClasses = 'border-red-300 focus:border-red-500 focus:ring-red-500';
  const disabledClasses = 'bg-gray-50 cursor-not-allowed';
  
  const classes = clsx(
    baseClasses,
    error && errorClasses,
    disabled && disabledClasses,
    className
  );
  
  return (
    <textarea
      ref={ref}
      rows={rows}
      className={classes}
      disabled={disabled}
      {...props}
    />
  );
});

Textarea.displayName = 'Textarea';

export default Textarea;


