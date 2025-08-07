import {StyleSheet, Dimensions} from 'react-native';

const {width, height} = Dimensions.get('window');

export const Colors = {
  primary: '#6200EE',
  primaryDark: '#3700B3',
  secondary: '#03DAC6',
  background: '#FFFFFF',
  surface: '#FFFFFF',
  error: '#B00020',
  onPrimary: '#FFFFFF',
  onSecondary: '#000000',
  onBackground: '#000000',
  onSurface: '#000000',
  onError: '#FFFFFF',
  success: '#4CAF50',
  warning: '#FF9800',
  info: '#2196F3',
  // Dark theme colors
  backgroundDark: '#121212',
  surfaceDark: '#1E1E1E',
  onBackgroundDark: '#FFFFFF',
  onSurfaceDark: '#FFFFFF',
};

export const Spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const FontSizes = {
  xs: 12,
  sm: 14,
  md: 16,
  lg: 18,
  xl: 22,
  xxl: 28,
};

export const BorderRadius = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
};

export const GlobalStyles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
    padding: Spacing.md,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: Colors.background,
    padding: Spacing.md,
  },
  card: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.md,
    marginVertical: Spacing.sm,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
  },
  button: {
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.md,
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.lg,
    alignItems: 'center',
    marginVertical: Spacing.sm,
  },
  buttonText: {
    color: Colors.onPrimary,
    fontSize: FontSizes.md,
    fontWeight: 'bold',
  },
  buttonSecondary: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: Colors.primary,
    borderRadius: BorderRadius.md,
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.lg,
    alignItems: 'center',
    marginVertical: Spacing.sm,
  },
  buttonSecondaryText: {
    color: Colors.primary,
    fontSize: FontSizes.md,
    fontWeight: 'bold',
  },
  input: {
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: BorderRadius.md,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    fontSize: FontSizes.md,
    backgroundColor: Colors.surface,
    marginVertical: Spacing.sm,
  },
  inputFocused: {
    borderColor: Colors.primary,
    borderWidth: 2,
  },
  title: {
    fontSize: FontSizes.xxl,
    fontWeight: 'bold',
    color: Colors.onBackground,
    textAlign: 'center',
    marginBottom: Spacing.lg,
  },
  subtitle: {
    fontSize: FontSizes.lg,
    fontWeight: '600',
    color: Colors.onBackground,
    marginBottom: Spacing.md,
  },
  text: {
    fontSize: FontSizes.md,
    color: Colors.onBackground,
    lineHeight: 22,
  },
  textSecondary: {
    fontSize: FontSizes.sm,
    color: '#757575',
    lineHeight: 20,
  },
  errorText: {
    color: Colors.error,
    fontSize: FontSizes.sm,
    marginTop: Spacing.xs,
  },
  successText: {
    color: Colors.success,
    fontSize: FontSizes.sm,
    marginTop: Spacing.xs,
  },
  listItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  listItemTitle: {
    fontSize: FontSizes.md,
    fontWeight: '600',
    color: Colors.onBackground,
  },
  listItemSubtitle: {
    fontSize: FontSizes.sm,
    color: '#757575',
    marginTop: Spacing.xs,
  },
  fab: {
    position: 'absolute',
    width: 56,
    height: 56,
    alignItems: 'center',
    justifyContent: 'center',
    right: 20,
    bottom: 20,
    backgroundColor: Colors.primary,
    borderRadius: 28,
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 4.65,
  },
  fabText: {
    fontSize: 24,
    color: Colors.onPrimary,
    fontWeight: 'bold',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: Colors.background,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: Spacing.xl,
  },
  emptyStateText: {
    fontSize: FontSizes.lg,
    color: '#757575',
    textAlign: 'center',
    marginTop: Spacing.md,
  },
});

export const getScreenWidth = () => width;
export const getScreenHeight = () => height;