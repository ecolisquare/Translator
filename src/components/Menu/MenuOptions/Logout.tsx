import React from 'react';
import LogoutIcon from '@icon/LogoutIcon';
import { useTranslation } from 'react-i18next';

const Logout = () => {
  const { t } = useTranslation();
  const handleLogout = () => {
    // 清除用户会话或本地存储中的用户数据（如有需要）
    // localStorage.removeItem('user');
    // sessionStorage.removeItem('user');

    // 跳转到指定的URL
    window.location.href = 'http://localhost:5173';
  };

  return (
    <a
      onClick={handleLogout} 
      className='flex py-3 px-3 items-center gap-3 rounded-md hover:bg-gray-500/10 transition-colors duration-200 text-white cursor-pointer text-sm'>
      <LogoutIcon />
      {t('LogOut')}
    </a>
  );
};

export default Logout;