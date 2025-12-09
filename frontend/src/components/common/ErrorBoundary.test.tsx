import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ErrorBoundary, ErrorFallback } from './ErrorBoundary';

/**
 * ErrorBoundary 单元测试
 * _Requirements: 9.4_
 */

// 用于测试的会抛出错误的组件
function ThrowError({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error('Test error message');
  }
  return <div>正常内容</div>;
}

describe('ErrorFallback', () => {
  it('应该显示错误信息', () => {
    const error = new Error('测试错误');
    render(<ErrorFallback error={error} />);
    
    expect(screen.getByText('出错了')).toBeInTheDocument();
    expect(screen.getByText('测试错误')).toBeInTheDocument();
  });

  it('应该显示刷新按钮', () => {
    render(<ErrorFallback />);
    
    expect(screen.getByRole('button', { name: '刷新页面' })).toBeInTheDocument();
  });

  it('点击刷新按钮应该调用 onRetry', () => {
    const onRetry = vi.fn();
    render(<ErrorFallback onRetry={onRetry} />);
    
    fireEvent.click(screen.getByRole('button', { name: '刷新页面' }));
    
    expect(onRetry).toHaveBeenCalledTimes(1);
  });
});

describe('ErrorBoundary', () => {
  // 抑制 React 的错误日志
  beforeEach(() => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  it('正常情况下应该渲染子组件', () => {
    render(
      <ErrorBoundary>
        <div>子组件内容</div>
      </ErrorBoundary>
    );
    
    expect(screen.getByText('子组件内容')).toBeInTheDocument();
  });

  it('发生错误时应该显示默认错误回退', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('出错了')).toBeInTheDocument();
    expect(screen.getByText('Test error message')).toBeInTheDocument();
  });

  it('发生错误时应该显示自定义回退', () => {
    render(
      <ErrorBoundary fallback={<div>自定义错误页面</div>}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('自定义错误页面')).toBeInTheDocument();
  });

  it('发生错误时应该调用 onError 回调', () => {
    const onError = vi.fn();
    
    render(
      <ErrorBoundary onError={onError}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(onError).toHaveBeenCalledTimes(1);
    expect(onError.mock.calls[0][0]).toBeInstanceOf(Error);
    expect(onError.mock.calls[0][0].message).toBe('Test error message');
  });
});
