import React, { useState } from 'react';
import { Input, Button, Form } from 'antd';
import { Link } from 'react-router-dom';
import './MyForm.css';
import axios from 'axios';

const Register = () => {
    const [form] = Form.useForm();
    const [isCodeButtonDisabled, setIsCodeButtonDisabled] = useState(true);
    const [isverify,setIsverify] = useState(false);
    const verification = "";

    const handleSubmit = (values: any) => {
        // 验证通过后的处理逻辑，可以将表单数据存储至React Redux和localStorage
        console.log(values);
        // if(verification == values.verificationCode){
        //     setIsverify(true);
        // }
        // axios.post('/register', {
        //     username: values.username,
        //     password: values.password,
        //     email: values.email,
        //   })
        //   .then(res => {
        //     if(res.data.status["code"] === 200 && isverify){
        //        alert("注册成功！")
        //     }
        //     else{
        //         alert(res.data.status["message"])
        //     }
        //   })
        //   .catch(err => {
        //     // 前后端传输数据错误，参照react标准处理
        //     console.log(err);
        //   })
    };

    const handleEmailChange = (e) => {
        const email = e.target.value;
        setIsCodeButtonDisabled(false);
    };

    const handleSendCode = () => {
        // 发送验证码逻辑
        console.log('Sending verification code...');
        // axios.post('/verification', {
        //     email: values.email,
        //   })
        //   .then(res => {
        //     if(res.data.status["code"] === 200){
        //        alert("验证码已发送！")
        //        verification = res.data.data["captcha"]
        //     else{
        //         alert(res.data.status["message"])
        //     }
        //   })
        //   .catch(err => {
        //     // 前后端传输数据错误，参照react标准处理
        //     console.log(err);
        //   })
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
                        rules={[{ required: true, message: '请输入验证码' }]}
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
                            // pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$/,
                            // message: '密码需包含至少1个大写字母、1个小写字母、1个数字和1个特殊字符',
                            pattern: /^(?:\d+|[a-zA-Z]+|[a-zA-Z\d]+)$/i,
                            message: '用户名为纯数字、纯英文字母或数字与英文字母组合',
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
                    {/* <Link to="/forget_password">忘记密码</Link> */}
                    <span>已有账号?<Link to="/login" >马上登录</Link></span>
                </div>
            </Form>
        </div>
    );
};

export default Register;
