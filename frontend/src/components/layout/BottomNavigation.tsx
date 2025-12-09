/**
 * 底部导航组件
 * 提供页面切换功能
 * 
 * _Requirements: 9.2_
 */

/**
 * 页面类型
 */
export type PageType = 'poster' | 'scene-fusion';

/**
 * 导航项配置
 */
interface NavItem {
  id: PageType;
  label: string;
  icon: string;
}

/**
 * 导航项列表
 */
const NAV_ITEMS: NavItem[] = [
  { id: 'poster', label: '海报生成', icon: '🎨' },
  { id: 'scene-fusion', label: '场景融合', icon: '🖼️' },
];

/**
 * BottomNavigation 组件属性
 */
interface BottomNavigationProps {
  /** 当前选中的页面 */
  currentPage: PageType;
  /** 页面切换回调 */
  onPageChange: (page: PageType) => void;
}

/**
 * 底部导航组件
 * 固定在页面底部中央，提供页面切换功能
 */
export function BottomNavigation({ currentPage, onPageChange }: BottomNavigationProps) {
  return (
    <nav className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50">
      <div className="flex gap-2 p-2 bg-gray-800/90 backdrop-blur-sm rounded-full border border-gray-700 shadow-lg">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            onClick={() => onPageChange(item.id)}
            className={`px-6 py-2 rounded-full text-sm font-medium transition-colors ${
              currentPage === item.id
                ? 'bg-red-600 text-white'
                : 'text-gray-300 hover:text-white hover:bg-gray-700'
            }`}
          >
            {item.icon} {item.label}
          </button>
        ))}
      </div>
    </nav>
  );
}

export default BottomNavigation;
