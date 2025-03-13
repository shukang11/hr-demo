import { serverAPI } from '../src/lib/api/client';
import { InsertCompany, createOrUpdateCompany } from '../src/lib/api/company';
import { InsertDepartment, createOrUpdateDepartment } from '../src/lib/api/department';
import { InsertPosition, createOrUpdatePosition } from '../src/lib/api/position';
import { InsertCandidate, createOrUpdateCandidate, CandidateStatus } from '../src/lib/api/candidate';
import { InsertEmployee, createOrUpdateEmployee, Gender } from '../src/lib/api/employee';

class TestDataGenerator {
  private companyId: number | null = null;
  private departments: { id: number; name: string }[] = [];
  private positions: { id: number; name: string }[] = [];
  private candidates: { id: number; name: string }[] = [];

  // 生成随机中文姓名
  private generateChineseName(): string {
    const surnames = ['张', '王', '李', '赵', '陈', '刘', '杨', '黄', '周', '吴'];
    const names = ['伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军'];
    return surnames[Math.floor(Math.random() * surnames.length)] + 
           names[Math.floor(Math.random() * names.length)];
  }

  // 生成随机手机号
  private generatePhone(): string {
    return '1' + Math.floor(Math.random() * 10) + 
           Array(9).fill(0).map(() => Math.floor(Math.random() * 10)).join('');
  }

  // 生成随机邮箱
  private generateEmail(name: string): string {
    const domains = ['qq.com', '163.com', 'gmail.com', 'outlook.com'];
    const domain = domains[Math.floor(Math.random() * domains.length)];
    return `${name}${Math.floor(Math.random() * 1000)}@${domain}`;
  }

  // 生成随机出生日期
  private generateBirthdate(): number {
    const start = new Date('1980-01-01').getTime();
    const end = new Date('2000-12-31').getTime();
    return start + Math.floor(Math.random() * (end - start));
  }

  // 生成随机地址
  private generateAddress(): string {
    const cities = ['北京市', '上海市', '广州市', '深圳市', '杭州市'];
    const districts = ['朝阳区', '浦东新区', '天河区', '南山区', '西湖区'];
    const streets = ['长安街', '南京路', '天河路', '深南大道', '西湖大道'];
    const city = cities[Math.floor(Math.random() * cities.length)];
    const district = districts[Math.floor(Math.random() * districts.length)];
    const street = streets[Math.floor(Math.random() * streets.length)];
    return `${city}${district}${street}${Math.floor(Math.random() * 100)}号`;
  }

  // 创建公司
  async createCompany() {
    console.log('开始创建公司...');
    const company: InsertCompany = {
      name: '未来科技有限公司',
      extra_value: {
        description: '一家专注于人工智能和机器学习的科技公司',
        address: '北京市朝阳区未来大厦',
        website: 'https://future-tech.com',
        phone: '010-12345678',
        email: 'contact@future-tech.com'
      }
    };

    try {
      const result = await createOrUpdateCompany(company);
      this.companyId = result.id;
      console.log('公司创建成功:', result);
    } catch (error) {
      console.error('创建公司失败:', error);
      throw error;
    }
  }

  // 创建部门
  async createDepartments() {
    if (!this.companyId) throw new Error('请先创建公司');

    console.log('开始创建部门...');
    const departmentNames = [
      '研发部',
      '产品部',
      '市场部',
      '销售部',
      '人力资源部',
      '财务部',
      '行政部'
    ];

    for (const name of departmentNames) {
      const department: InsertDepartment = {
        name,
        company_id: this.companyId,
        remark: `${name}负责公司的${name.replace('部', '')}相关工作`
      };

      try {
        const result = await createOrUpdateDepartment(department);
        this.departments.push({ id: result.id, name: result.name });
        console.log(`部门 ${name} 创建成功`);
      } catch (error) {
        console.error(`创建部门 ${name} 失败:`, error);
      }
    }
  }

  // 创建职位
  async createPositions() {
    if (!this.companyId) throw new Error('请先创建公司');
    if (this.departments.length === 0) throw new Error('请先创建部门');

    console.log('开始创建职位...');
    const positions = [
      { name: '软件工程师', department: '研发部' },
      { name: '产品经理', department: '产品部' },
      { name: '市场专员', department: '市场部' },
      { name: '销售经理', department: '销售部' },
      { name: 'HR专员', department: '人力资源部' },
      { name: '财务主管', department: '财务部' },
      { name: '行政助理', department: '行政部' }
    ];

    for (const pos of positions) {
      const department = this.departments.find(d => d.name === pos.department);
      if (!department) continue;

      const position: InsertPosition = {
        name: pos.name,
        company_id: this.companyId,
        remark: `${pos.department}的${pos.name}岗位`
      };

      try {
        const result = await createOrUpdatePosition(position);
        this.positions.push({ id: result.id, name: result.name });
        console.log(`职位 ${pos.name} 创建成功`);
      } catch (error) {
        console.error(`创建职位 ${pos.name} 失败:`, error);
      }
    }
  }

  // 创建候选人
  async createCandidates(count: number = 100) {
    if (!this.companyId) throw new Error('请先创建公司');
    if (this.departments.length === 0) throw new Error('请先创建部门');
    if (this.positions.length === 0) throw new Error('请先创建职位');

    console.log(`开始创建 ${count} 个候选人...`);
    for (let i = 0; i < count; i++) {
      const name = this.generateChineseName();
      const position = this.positions[Math.floor(Math.random() * this.positions.length)];
      const department = this.departments[Math.floor(Math.random() * this.departments.length)];

      const candidate: InsertCandidate = {
        company_id: this.companyId,
        name,
        phone: this.generatePhone(),
        email: this.generateEmail(name),
        position_id: position.id,
        department_id: department.id,
        interview_date: new Date().toISOString(),
        remark: `应聘${position.name}岗位`
      };

      try {
        const result = await createOrUpdateCandidate(candidate);
        this.candidates.push({ id: result.id, name: result.name });
        console.log(`候选人 ${name} 创建成功 (${i + 1}/${count})`);
      } catch (error) {
        console.error(`创建候选人 ${name} 失败:`, error);
      }
    }
  }

  // 创建员工（从候选人转化）
  async createEmployees(count: number = 40) {
    if (!this.companyId) throw new Error('请先创建公司');
    if (this.candidates.length === 0) throw new Error('请先创建候选人');

    console.log(`开始创建 ${count} 个员工...`);
    const selectedCandidates = this.candidates.slice(0, count);

    for (let i = 0; i < selectedCandidates.length; i++) {
      const candidate = selectedCandidates[i];
      const position = this.positions[Math.floor(Math.random() * this.positions.length)];
      const department = this.departments[Math.floor(Math.random() * this.departments.length)];

      const employee: InsertEmployee = {
        company_id: this.companyId,
        name: candidate.name,
        email: this.generateEmail(candidate.name),
        phone: this.generatePhone(),
        birthdate: this.generateBirthdate(),
        address: this.generateAddress(),
        gender: Math.random() > 0.5 ? 'Male' : 'Female',
        department_id: department.id,
        position_id: position.id,
        entry_date: Date.now(),
        candidate_id: candidate.id
      };

      try {
        const result = await createOrUpdateEmployee(employee);
        console.log(`员工 ${candidate.name} 创建成功 (${i + 1}/${count})`);

        // 更新候选人状态为已录用
        await serverAPI.post(`candidate/${candidate.id}/status`, {
          json: {
            status: CandidateStatus.Accepted,
            evaluation: '面试通过，已录用',
            remark: `转为正式员工，入职日期：${new Date().toLocaleDateString()}`
          }
        });
      } catch (error) {
        console.error(`创建员工 ${candidate.name} 失败:`, error);
      }
    }
  }
}

async function main() {
  console.log('开始生成测试数据...\n');
  const generator = new TestDataGenerator();

  try {
    // 1. 创建公司
    await generator.createCompany();
    console.log('');

    // 2. 创建部门
    await generator.createDepartments();
    console.log('');

    // 3. 创建职位
    await generator.createPositions();
    console.log('');

    // 4. 创建候选人
    await generator.createCandidates(100);
    console.log('');

    // 5. 创建员工
    await generator.createEmployees(40);
    console.log('');

    console.log('测试数据生成完成！');
  } catch (error) {
    console.error('生成测试数据失败:', error);
    process.exit(1);
  }
}

main(); 