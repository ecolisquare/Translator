import ArrowBottom from "@icon/ArrowBottom";
import React, { ChangeEvent, useState } from 'react';
import PopupModal from "@components/PopupModal";
import useStore from "@store/store";
import { UserPromptInterface } from "@type/userpref";
import UserPromptConfig from "./UserPromptConfig";
import DstLanguageSelector from "@components/DstLanguageSelector";
import { t } from "i18next";

const UserPromptBar = () => {
    const [inputValue, setInputValue] = useState<string>('');
    const [showPromptPopup, setShowPromptPopup] = useState<boolean>(false);

    const currentChatIndex = useStore((state) => state.currentChatIndex);
    const chats = useStore((state) => state.chats);
    if (!chats || currentChatIndex < 0 || currentChatIndex >= chats.length) return <></>;

    const userPrompts = useStore((state) => state.userPrompts);
    const setUserPrompts = useStore((state) => state.setUserPrompts);

    const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
        setInputValue(e.target.value)
    }

    const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        const isMobile =
            /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini|playbook|silk/i.test(
                navigator.userAgent
            );

        if (e.key === 'Enter' && !isMobile && !e.nativeEvent.isComposing) {
            if (e.ctrlKey && e.shiftKey) {
                e.preventDefault();
            } else {
                // Add to userPrompt
                const updatedUserPrompts: UserPromptInterface[] = JSON.parse(JSON.stringify(userPrompts));
                // updatedUserPrompts = []; // clear all prompts, for debug
                updatedUserPrompts.push({
                    content: inputValue
                });
                setUserPrompts(updatedUserPrompts);
                setInputValue('');
            }
        }
    }

    const validateUserPrompt = () => {
        // Remove Empty Entries
        // const updatedUserPrompts: UserPromptInterface[] = JSON.parse(JSON.stringify(userDicts));
        const updatedUserPrompts = userPrompts.filter((prompt) => prompt.content);
        setUserPrompts(updatedUserPrompts);
    };

    return (
        <>
            <div
                className={'flex items-center gap-2'}
                style={{
                    'borderWidth': '0.5px',
                    'borderColor': 'rgba(0,0,0,0)',
                    'flex': '1',
                }}>
                {/* <div className='flex w-[calc(100%-36px)]'>
                    <UserPromptInputBar
                        value={inputValue}
                        handleChange={handleInputChange}
                        handleKeyDown={handleInputKeyDown}
                        className={"w-full"}
                        disabled={false}
                    />
                </div> */}
                <button className="btn relative mr-2 btn-primary"
                    // style={{
                    //     'justifyContent': 'center',
                    //     'margin': '0',
                    //     'border': 'none',
                    // }}
                    onClick={() => setShowPromptPopup(!showPromptPopup)}
                >
                    <div className='flex items-center justify-center gap-2'>
                        {t('StyleEdit')}
                    </div>
                    {/* Dropup Toggle for Dictionary Menu */}
                    {/* <ArrowBottom className={`transition-all duration-100 ${showPromptPopup ? '' : 'rotate-180'}`} /> */}
                    {/* <SettingIcon /> */}
                </button>
                <DstLanguageSelector />
            </div>
            {showPromptPopup && <PopupModal
                title={t('StyleEdit') as string}
                message={''}
                setIsModalOpen={setShowPromptPopup}
                handleConfirm={() => { validateUserPrompt(); setShowPromptPopup(false); }}
                handleClose={validateUserPrompt}
                cancelButton={false}
            >
                <UserPromptConfig />
            </PopupModal>}
        </>
    );
};

const UserPromptInputBar = ({
    value,
    handleChange,
    handleKeyDown,
    className,
    disabled,
}: {
    value: string;
    handleChange: React.ChangeEventHandler<HTMLInputElement>;
    handleKeyDown: React.KeyboardEventHandler<HTMLInputElement>;
    className?: React.HTMLAttributes<HTMLDivElement>['className'];
    disabled?: boolean;
}) => {
    return (
        <div className={className}>
            <input
                disabled={disabled}
                type='text'
                className='text-gray-800 dark:text-white p-3 text-sm bg-transparent disabled:opacity-40  disabled:cursor-not-allowed transition-opacity m-0 w-full h-full focus:outline-none rounded border border-white/20'
                placeholder={'输入自定义Prompt'}
                value={value}
                onChange={(e) => { handleChange(e) }}
                onKeyDown={(e) => { handleKeyDown(e) }}
            />
        </div>
    );
};

export default UserPromptBar;