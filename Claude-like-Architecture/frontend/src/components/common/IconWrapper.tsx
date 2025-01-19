import React from 'react';
import { LucideProps, LucideIcon } from 'lucide-react';

interface IconWrapperProps extends Omit<LucideProps, 'ref'> {
  icon: LucideIcon;
}

export const IconWrapper = ({ icon: Icon, ...props }: IconWrapperProps) => {
  return <Icon {...props} />;
};