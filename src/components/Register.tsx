import React, { useState } from 'react';
import { Input, Button, Form } from 'antd';
import { Link } from 'react-router-dom';
import './MyForm.css';
import axios from 'axios';

const Register = () => {
    const [form] = Form.useForm();
    const [isCodeButtonDisabled, setIsCodeButtonDisabled] = useState(true);
    const [isVerify, setIsVerify] = useState(false);
    const [verification, setVerification] = useState('');

    const handleSubmit = (values: any) => {
        console.log(values);
        console.log(verification);
        if (verification === values.verificationCode) {
            setIsVerify(true);
        } else {
            alert("验证码错误");
            return;
        }

        axios.post('/register', {
            username: values.username,
            password: values.password,
            email: values.email,
        })
        .then(res => {
            if (res.data.status.code === 200 && isVerify) {
                alert("注册成功！");
            } else {
                alert(res.data.status.message);
            }
        })
        .catch(err => {
            console.log(err);
        });
    };

    const handleEmailChange = (e) => {
        const email = e.target.value;
        form.setFieldsValue({ email });
        setIsCodeButtonDisabled(false);
    };

    const handleSendCode = () => {
        const email = form.getFieldValue('email');
        if (!email) {
            alert("请先输入邮箱");
            return;
        }

        console.log('Sending verification code...');
        axios.post('/verification', {
            email: email,
        })
        .then(res => {
            if (res.data.status.code === 200) {
                alert("验证码已发送！");
                setVerification(res.data.data.captcha);
            } else {
                alert(res.data.status.message);
            }
        })
        .catch(err => {
            console.log(err);
        });
    };

    return (
        <div className="form_container">
            <Form form={form} onFinish={handleSubmit} className="custom_form">
                <h2>用户注册</h2>
                <Form.Item
                    name="username"
                    rules={[
                        { required: true, message: '请输入用户名' },
                        { max: 6, message: '用户名不超过6位' },
                        {
                            pattern: /^(?:\d+|[a-zA-Z]+|[a-zA-Z\d]+)$/i,
                            message: '用户名为纯数字、纯英文字母或数字与英文字母组合',
                        },
                    ]}
                >
                    <Input placeholder="请输入用户名"/>
                </Form.Item>
                <Form.Item
                    name="email"
                    rules={[
                        { required: true, message: '请输入邮箱' },
                        {
                            pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
                            message: '请输入有效的邮箱',
                        },
                    ]}
                >
                    <Input placeholder="请输入邮箱" onChange={handleEmailChange} />
                </Form.Item>
                <div className='verificationArea'>
                    <Form.Item
                        name="verificationCode"
                        className='verificationCode'
                        rules={[{ required: true, message: '请输入验证码' },
                                { len: 6, message: '验证码必须为6位' },
                        ]}
                    >
                        <Input placeholder="请输入验证码"/>
                    </Form.Item>
                    <Form.Item>
                        <Button 
                            type="primary" 
                            className='verificationCode_button' 
                            onClick={handleSendCode} 
                            disabled={isCodeButtonDisabled}
                        >
                            发送验证码
                        </Button>
                    </Form.Item>
                </div>
                <Form.Item
                    name="password"
                    rules={[
                        { required: true, message: '请输入密码' },
                        { min: 6, message: '密码最少6位' },
                        {
                            pattern: /^(?:\d+|[a-zA-Z]+|[a-zA-Z\d]+)$/i,
                            message: '密码为纯数字、纯英文字母或数字与英文字母组合',
                        },
                    ]}
                >
                    <Input.Password placeholder="请输入密码"/>
                </Form.Item>
                <Form.Item>
                    <Button type="primary" htmlType="submit" className='submitButton'>
                        立即注册
                    </Button>
                </Form.Item>
                <div className='toRouter'>
                    <span>已有账号?<Link to="/login">马上登录</Link></span>
                </div>
            </Form>
        </div>
    );
};

export default Register;
