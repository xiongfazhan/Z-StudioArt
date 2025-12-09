import { Component } from 'react';
import type { ReactNode, ErrorInfo } from 'react';

/**
 * 错误回退组件的属性
 */
interface ErrorFallbackProps {
  error?: Error;
  onRetry?: () => void;
}

/**
 * 错误回退组件 - 当发生错误时显示友好的错误页面
 */
export function ErrorFallback({ error, onRetry }: ErrorFallbackProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <div className="text-center p-8 max-w-md">
        <div className="text-red-500 text-6xl mb-4">⚠️</div>
        <h1 className="text-2xl font-bold text-white mb-4">出错了</h1>
        <p className="text-gray-400 mb-6">
          抱歉，页面发生了一些问题。请尝试刷新页面或稍后再试。
        </p>
        {error && (
          <details className="text-left mb-6 p-4 bg-gray-800 rounded-lg">
            <summary className="text-gray-300 cursor-pointer">错误详情</summary>
            <pre className="mt-2 text-sm text-red-400 overflow-auto">
              {error.message}
            </pre>
          </details>
        )}
        <button
          onClick={onRetry || (() => window.location.reload())}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          刷新页面
        </button>
      </div>
    </div>
  );
}

/**
 * ErrorBoundary 组件属性
 */
interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

/**
 * ErrorBoundary 组件状态
 */
interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

/**
 * 错误边界组件 - 捕获子组件树中的 JavaScript 错误
 * 
 * 使用方式:
 * ```tsx
 * <ErrorBoundary>
 *   <YourComponent />
 * </ErrorBoundary>
 * ```
 * 
 * 或者使用自定义回退:
 * ```tsx
 * <ErrorBoundary fallback={<CustomErrorPage />}>
 *   <YourComponent />
 * </ErrorBoundary>
 * ```
 * 
 * _Requirements: 9.4_
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('Error caught by ErrorBoundary:', error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  handleRetry = (): void => {
    this.setState({ hasError: false, error: undefined });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return <ErrorFallback error={this.state.error} onRetry={this.handleRetry} />;
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
