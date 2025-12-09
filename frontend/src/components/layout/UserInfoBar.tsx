/**
 * 用户信息栏组件
 * 显示用户信息、会员等级和快捷操作按钮
 * 
 * _Requirements: 9.1_
 */

import { useNavigate } from 'react-router-dom';
import { getMembershipConfig } from '../../utils/membership';
import type { User } from '../../types';

/**
 * UserInfoBar 组件属性
 */
interface UserInfoBarProps {
  /** 当前登录用户 */
  user: User;
  /** 退出登录回调 */
  onLogout: () => void;
}

/**
 * 用户信息栏组件
 * 固定在页面右上角，显示用户信息和操作按钮
 */
export function UserInfoBar({ user, onLogout }: UserInfoBarProps) {
  const navigate = useNavigate();
  const membershipConfig = getMembershipConfig(user.membership_tier);

  return (
    <div className="fixed top-4 right-4 z-50 flex items-center gap-3">
      <div className="px-4 py-2 bg-gray-800/90 backdrop-blur-sm rounded-full border border-gray-700 shadow-lg flex items-center gap-3">
        {/* 用户标识 */}
        <span className="text-sm text-gray-300">
          {user.phone || user.email}
        </span>
        
        {/* 会员等级标签 */}
        <button
          onClick={() => navigate('/subscription')}
          className={`text-xs px-2 py-0.5 rounded-full cursor-pointer hover:opacity-80 transition-opacity ${membershipConfig.style}`}
          title="会员订阅"
        >
          {membershipConfig.label}
        </button>
        
        {/* 历史记录按钮 */}
        <button
          onClick={() => navigate('/history')}
          className="text-sm text-gray-400 hover:text-white transition-colors"
          title="生成历史"
        >
          📜
        </button>
        
        {/* 订阅按钮 */}
        <button
          onClick={() => navigate('/subscription')}
          className="text-sm text-gray-400 hover:text-white transition-colors"
          title="会员订阅"
        >
          👑
        </button>
        
        {/* 退出登录按钮 */}
        <button
          onClick={onLogout}
          className="text-sm text-gray-400 hover:text-white transition-colors"
          title="退出登录"
        >
          退出
        </button>
      </div>
    </div>
  );
}

export default UserInfoBar;
