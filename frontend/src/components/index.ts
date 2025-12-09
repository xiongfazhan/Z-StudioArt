/**
 * 组件导出索引
 */

// 通用组件
export { ErrorBoundary, ErrorFallback } from './common/ErrorBoundary';

// 布局组件
export { UserInfoBar } from './layout/UserInfoBar';
export { BottomNavigation } from './layout/BottomNavigation';
export type { PageType } from './layout/BottomNavigation';

// 输入组件
export { SceneDescriptionInput } from './SceneDescriptionInput';
export { MarketingTextInput } from './MarketingTextInput';
export { TemplateSelector } from './TemplateSelector';
export { AspectRatioSelector } from './AspectRatioSelector';
export { ProductImageUpload } from './ProductImageUpload';

// 展示组件
export { ResultGallery } from './ResultGallery';

// 页面组件
export { PosterGeneratorPage } from './PosterGeneratorPage';
export { SceneFusionPage } from './SceneFusionPage';

// 路由组件
export { ProtectedRoute, PublicRoute } from './ProtectedRoute';

// 模态框组件
export { ImageDetailModal } from './ImageDetailModal';
export { PaymentModal } from './PaymentModal';
