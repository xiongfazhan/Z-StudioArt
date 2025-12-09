/**
 * 会员配置模块
 * 定义会员等级的样式和标签配置
 * 
 * Requirements: 9.3
 */

import type { MembershipTier } from '../types';

/**
 * 会员配置接口
 */
export interface MembershipConfig {
  label: string;
  style: string;
}

/**
 * 会员配置常量
 * 包含所有会员等级的标签和样式定义
 */
export const MEMBERSHIP_CONFIG: Record<MembershipTier, MembershipConfig> = {
  professional: {
    label: '专业版',
    style: 'bg-purple-500/20 text-purple-300 border border-purple-500/30',
  },
  basic: {
    label: '基础版',
    style: 'bg-blue-500/20 text-blue-300 border border-blue-500/30',
  },
  free: {
    label: '免费版',
    style: 'bg-gray-500/20 text-gray-300 border border-gray-500/30',
  },
} as const;

/**
 * 所有有效的会员等级
 */
export const MEMBERSHIP_TIERS: MembershipTier[] = ['free', 'basic', 'professional'];

/**
 * 获取会员配置
 * @param tier 会员等级字符串
 * @returns 对应的会员配置，如果等级无效则返回免费版配置
 */
export function getMembershipConfig(tier: string): MembershipConfig {
  if (tier in MEMBERSHIP_CONFIG) {
    return MEMBERSHIP_CONFIG[tier as MembershipTier];
  }
  return MEMBERSHIP_CONFIG.free;
}

/**
 * 检查是否为有效的会员等级
 * @param tier 待检查的字符串
 * @returns 是否为有效的会员等级
 */
export function isValidMembershipTier(tier: string): tier is MembershipTier {
  return MEMBERSHIP_TIERS.includes(tier as MembershipTier);
}
