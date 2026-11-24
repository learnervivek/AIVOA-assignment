import { configureStore } from '@reduxjs/toolkit';
import rcaReducer from './slices/rcaSlice';
import aiPanelReducer from './slices/aiPanelSlice';

export const store = configureStore({
  reducer: {
    rca: rcaReducer,
    aiPanel: aiPanelReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
