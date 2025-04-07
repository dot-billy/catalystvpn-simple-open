// Optional performance monitoring
const reportWebVitals = (onPerfEntry?: any) => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    try {
      import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
        getCLS(onPerfEntry);
        getFID(onPerfEntry);
        getFCP(onPerfEntry);
        getLCP(onPerfEntry);
        getTTFB(onPerfEntry);
      }).catch(() => {
        // Silently fail if web-vitals is not available
        console.log('Performance monitoring is not available');
      });
    } catch (error) {
      // Silently fail if web-vitals is not available
      console.log('Performance monitoring is not available');
    }
  }
};

export default reportWebVitals; 