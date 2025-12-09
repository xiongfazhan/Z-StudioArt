/**
 * 会员配置模块测试
 * 
 * **Feature: system-optimization, Property 9: 会员配置完整性**
 * **Validates: Requirements 9.3**
 */

import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';
import {
  MEMBERSHIP_CONFIG,
  MEMBERSHIP_TIERS,
  getMembershipConfig,
  isValidMembershipTier,
} from './membership';

describe('MEMBERSHIP_CONFIG', () => {
  /**
   * **Feature: system-optimization, Property 9: 会员配置完整性**
   * **Validates: Requirements 9.3**
   * 
   * *For any* 会员等级（free, basic, professional），MEMBERSHIP_CONFIG 应包含对应的 label 和 style
   */
  it('属性测试：所有会员等级都应包含 label 和 style', () => {
    fc.assert(
      fc.property(
        fc.constantFrom(...MEMBERSHIP_TIERS),
        (tier) => {
          const config = MEMBERSHIP_CONFIG[tier];
          
          // 配置必须存在
          expect(config).toBeDefined();
          
          // 必须包含 label 属性且为非空字符串
          expect(typeof config.label).toBe('string');
          expect(config.label.length).toBeGreaterThan(0);
          
          // 必须包含 style 属性且为非空字符串
          expect(typeof config.style).toBe('string');
          expect(config.style.length).toBeGreaterThan(0);
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该包含所有三个会员等级的配置', () => {
    expect(MEMBERSHIP_CONFIG).toHaveProperty('free');
    expect(MEMBERSHIP_CONFIG).toHaveProperty('basic');
    expect(MEMBERSHIP_CONFIG).toHaveProperty('professional');
  });

  it('每个配置应该有正确的中文标签', () => {
    expect(MEMBERSHIP_CONFIG.free.label).toBe('免费版');
    expect(MEMBERSHIP_CONFIG.basic.label).toBe('基础版');
    expect(MEMBERSHIP_CONFIG.professional.label).toBe('专业版');
  });

  it('每个配置应该有有效的 Tailwind CSS 样式类', () => {
    for (const tier of MEMBERSHIP_TIERS) {
      const config = MEMBERSHIP_CONFIG[tier];
      // 样式应该包含背景色、文字色和边框
      expect(config.style).toMatch(/bg-/);
      expect(config.style).toMatch(/text-/);
      expect(config.style).toMatch(/border/);
    }
  });
});

describe('getMembershipConfig', () => {
  /**
   * **Feature: system-optimization, Property 9: 会员配置完整性**
   * **Validates: Requirements 9.3**
   * 
   * 属性测试：对于任意有效会员等级，getMembershipConfig 应返回正确的配置
   */
  it('属性测试：有效会员等级应返回对应配置', () => {
    fc.assert(
      fc.property(
        fc.constantFrom(...MEMBERSHIP_TIERS),
        (tier) => {
          const config = getMembershipConfig(tier);
          const expected = MEMBERSHIP_CONFIG[tier];
          
          expect(config).toEqual(expected);
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * 属性测试：对于任意无效字符串，getMembershipConfig 应返回免费版配置
   */
  it('属性测试：无效会员等级应返回免费版配置', () => {
    fc.assert(
      fc.property(
        fc.string().filter(s => !MEMBERSHIP_TIERS.includes(s as any)),
        (invalidTier) => {
          const config = getMembershipConfig(invalidTier);
          
          expect(config).toEqual(MEMBERSHIP_CONFIG.free);
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该为有效等级返回正确配置', () => {
    expect(getMembershipConfig('free')).toEqual(MEMBERSHIP_CONFIG.free);
    expect(getMembershipConfig('basic')).toEqual(MEMBERSHIP_CONFIG.basic);
    expect(getMembershipConfig('professional')).toEqual(MEMBERSHIP_CONFIG.professional);
  });

  it('应该为无效等级返回免费版配置', () => {
    expect(getMembershipConfig('invalid')).toEqual(MEMBERSHIP_CONFIG.free);
    expect(getMembershipConfig('')).toEqual(MEMBERSHIP_CONFIG.free);
    expect(getMembershipConfig('premium')).toEqual(MEMBERSHIP_CONFIG.free);
  });
});

describe('isValidMembershipTier', () => {
  /**
   * 属性测试：MEMBERSHIP_TIERS 中的所有值都应该是有效的会员等级
   */
  it('属性测试：已定义的会员等级应该有效', () => {
    fc.assert(
      fc.property(
        fc.constantFrom(...MEMBERSHIP_TIERS),
        (tier) => {
          return isValidMembershipTier(tier) === true;
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * 属性测试：不在 MEMBERSHIP_TIERS 中的字符串应该无效
   */
  it('属性测试：未定义的字符串应该无效', () => {
    fc.assert(
      fc.property(
        fc.string().filter(s => !MEMBERSHIP_TIERS.includes(s as any)),
        (invalidTier) => {
          return isValidMembershipTier(invalidTier) === false;
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该正确识别有效的会员等级', () => {
    expect(isValidMembershipTier('free')).toBe(true);
    expect(isValidMembershipTier('basic')).toBe(true);
    expect(isValidMembershipTier('professional')).toBe(true);
  });

  it('应该正确拒绝无效的会员等级', () => {
    expect(isValidMembershipTier('invalid')).toBe(false);
    expect(isValidMembershipTier('')).toBe(false);
    expect(isValidMembershipTier('premium')).toBe(false);
    expect(isValidMembershipTier('FREE')).toBe(false); // 大小写敏感
  });
});

describe('MEMBERSHIP_TIERS', () => {
  it('应该包含正好三个会员等级', () => {
    expect(MEMBERSHIP_TIERS).toHaveLength(3);
  });

  it('应该包含所有预期的会员等级', () => {
    expect(MEMBERSHIP_TIERS).toContain('free');
    expect(MEMBERSHIP_TIERS).toContain('basic');
    expect(MEMBERSHIP_TIERS).toContain('professional');
  });
});
