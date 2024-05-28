import React from 'react';
import { Input, Button, Form } from 'antd';
import { Link } from 'react-router-dom';
import axios from 'axios';

const Login = () => {
    const [form] = Form.useForm();

    // const handleSubmit = async (values: any) => {
    //     console.log(values);
    //     const userId = values.username;
    //     // 构建带有查询参数的URL
    //     // const url = `http://localhost:5174?userId=${userId}`;
    //     // 跳转到指定的URL
    //     // window.location.href = url;

    //     axios.interceptors.request.use(request => {
    //         console.log('Starting Request');
    //         console.log('URL:', request.url);
    //         console.log('Method:', request.method);
    //         console.log('Headers:', JSON.stringify(request.headers, null, 2));
    //         console.log('Data:', request.data);
    //         return request;
    //     }, error => {
    //         console.error('Request Error:', error);
    //         return Promise.reject(error);
    //     });
    //     const config = {
    //         headers: {
    //             'Access-Control-Allow-Origin' : 'http://localhost:5173',
    //             'Access-Control-Allow-Methods':'GET,PUT,POST,DELETE,PATCH,OPTIONS',
    //             'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    //         }
    //     };

    //     axios.post('http://10.219.227.52:5000/auth/login', 
    //         {
    //             username: values.username,
    //             password: values.password,
    //         },
    //         config
    //     )
    //       .then(res => {
    //         if(res.data.status["statusCode"] === 0){
    //             const url = `http://localhost:5174?userId=${userId}`;
    //             // 跳转到指定的URL
    //             window.location.href = url;
    //         }
    //         else{
    //             alert(res.data.status["message"])
    //         }
    //       })
    //       .catch(err => {
    //         // 前后端传输数据错误，参照react标准处理
    //         console.log(err);
    //       })
    // };
    const handleSubmit = async (values) => {
        console.log(values);
        const userId = values.username;
            axios.interceptors.request.use(request => {
            console.log('Starting Request');
            console.log('URL:', request.url);
            console.log('Method:', request.method);
            console.log('Headers:', JSON.stringify(request.headers, null, 2));
            console.log('Data:', request.data);
            return request;
        }, error => {
            console.error('Request Error:', error);
            return Promise.reject(error);
        });
    
        try {
            const response = await axios.post('/auth/login', {
                username: values.username,
                password: values.password,
            });
    
            if (response.data.status["statusCode"] === 0) {
                const url = `http://localhost:5174?userId=${userId}`;
                // 跳转到指定的URL
                window.location.href = url;
            } else {
                alert(response.data.status["message"]);
            }
        } catch (error) {
            console.error('Error in request:', error);
        }
    };

    return (
        <div className="form_container">
            <Form form={form} onFinish={handleSubmit} className="custom_form">
                <h2>登录</h2>
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
                    name="password"
                    rules={[
                        { required: true, message: '请输入密码' },
                        { min: 6, message: '密码最少6位' },
                        {
                            // pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$/,
                            pattern: /^(?:\d+|[a-zA-Z]+|[a-zA-Z\d]+)$/i,
                            message: '密码为纯数字、纯英文字母或数字与英文字母组合',
                        },
                    ]}
                >
                    <Input.Password placeholder="请输入密码"/>
                </Form.Item>
                <Form.Item>
                    <Button type="primary" htmlType="submit" className='submitButton'>
                        登录
                    </Button>
                </Form.Item>
                <div className='toRouter'>
                    {/* <Link to="/forget_password">忘记密码</Link> */}
                    <span>没有账号?<Link to="/register" >快速注册</Link></span>
                </div>
            </Form>
        </div>
    );
};

export default Login;
