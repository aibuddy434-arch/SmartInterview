import React from 'react';
import { clsx } from 'clsx';

const Card = React.forwardRef(({
  children,
  className = '',
  ...props
}, ref) => {
  const classes = clsx(
    'bg-white overflow-hidden shadow rounded-lg',
    className
  );
  
  return (
    <div
      ref={ref}
      className={classes}
      {...props}
    >
      {children}
    </div>
  );
});

Card.displayName = 'Card';

const CardHeader = React.forwardRef(({
  children,
  className = '',
  ...props
}, ref) => {
  const classes = clsx(
    'px-4 py-5 sm:p-6',
    className
  );
  
  return (
    <div
      ref={ref}
      className={classes}
      {...props}
    >
      {children}
    </div>
  );
});

CardHeader.displayName = 'CardHeader';

const CardBody = React.forwardRef(({
  children,
  className = '',
  ...props
}, ref) => {
  const classes = clsx(
    'px-4 py-5 sm:p-6',
    className
  );
  
  return (
    <div
      ref={ref}
      className={classes}
      {...props}
    >
      {children}
    </div>
  );
});

CardBody.displayName = 'CardBody';

const CardFooter = React.forwardRef(({
  children,
  className = '',
  ...props
}, ref) => {
  const classes = clsx(
    'px-4 py-4 sm:px-6 bg-gray-50',
    className
  );
  
  return (
    <div
      ref={ref}
      className={classes}
      {...props}
    >
      {children}
    </div>
  );
});

CardFooter.displayName = 'CardFooter';

export { Card, CardHeader, CardBody, CardFooter };


