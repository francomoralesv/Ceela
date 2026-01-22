// This file handles imports that should only be loaded on the client side

export const loadJQuery = async () => {
  if (typeof window !== 'undefined') {
    try {
      await import('public/assets/js/jquery.min.js');
      return true;
    } catch (error) {
      console.error('Error loading jQuery:', error);
      return false;
    }
  }
  return false;
};