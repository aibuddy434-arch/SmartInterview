import React from 'react';
import { clsx } from 'clsx';

const Checkbox = React.forwardRef(({
  children,
  className = '',
  error = false,
  disabled = false,
  ...props
}, ref) => {
  const baseClasses = 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded transition-colors';
  const errorClasses = 'border-red-300 focus:ring-red-500';
  const disabledClasses = 'bg-gray-100 cursor-not-allowed';
  
  const classes = clsx(
    baseClasses,
    error && errorClasses,
    disabled && disabledClasses,
    className
  );
  
  return (
    <div className="flex items-center">
      <input
        ref={ref}
        type="checkbox"
        className={classes}
        disabled={disabled}
        {...props}
      />
      {children && (
        <label className="ml-2 block text-sm text-gray-900">
          {children}
        </label>
      )}
    </div>
  );
});

Checkbox.displayName = 'Checkbox';

export default Checkbox;


