import { ComponentProps } from 'react';
import { GridBaseProps, GridSize, GridSpacing } from '@mui/material';

declare module '@mui/material' {
  interface GridProps extends GridBaseProps {
    item?: boolean;
    container?: boolean;
    spacing?: GridSpacing;
    xs?: GridSize;
    sm?: GridSize;
    md?: GridSize;
    lg?: GridSize;
    xl?: GridSize;
  }

  export function Grid(props: GridProps): JSX.Element;
} 