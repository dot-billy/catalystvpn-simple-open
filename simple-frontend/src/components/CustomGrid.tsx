import React from 'react';
import { Grid as MuiGrid, GridProps as MuiGridProps, GridSize } from '@mui/material';
import { SxProps, Theme } from '@mui/system';

export interface GridProps extends Omit<MuiGridProps, 'xs' | 'sm' | 'md' | 'lg' | 'xl'> {
  item?: boolean;
  container?: boolean;
  spacing?: number | string;
  xs?: boolean | GridSize;
  sm?: boolean | GridSize;
  md?: boolean | GridSize;
  lg?: boolean | GridSize;
  xl?: boolean | GridSize;
  sx?: SxProps<Theme>;
}

const Grid: React.FC<GridProps> = (props) => {
  return <MuiGrid {...props} />;
};

export default Grid; 