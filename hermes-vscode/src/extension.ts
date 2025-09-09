import * as vscode from 'vscode';
import { ZSCEAgentProvider } from './zsceAgentProvider';
import { WorkflowManager } from './workflowManager';
import { ConstitutionViewer } from './constitutionViewer';

export function activate(context: vscode.ExtensionContext) {
    console.log('ZSCE Agent extension is now active!');

    // 创建工作流管理器
    const workflowManager = new WorkflowManager();
    
    // 创建宪法查看器
    const constitutionViewer = new ConstitutionViewer();

    // 注册命令
    let startWorkflow = vscode.commands.registerCommand('zswe-agent.startWorkflow', async () => {
        await workflowManager.startWorkflow();
    });

    let viewWorkflowStatus = vscode.commands.registerCommand('zswe-agent.viewWorkflowStatus', () => {
        workflowManager.showWorkflowStatus();
    });

    let openConstitution = vscode.commands.registerCommand('zswe-agent.openConstitution', () => {
        constitutionViewer.openConstitution();
    });

    // 注册视图提供者
    const zsceAgentProvider = new ZSCEAgentProvider(workflowManager);
    vscode.window.registerTreeDataProvider('zsweAgentWorkflow', zsceAgentProvider);

    // 添加到订阅列表
    context.subscriptions.push(startWorkflow, viewWorkflowStatus, openConstitution);
}

export function deactivate() {
    console.log('ZSCE Agent extension is now deactivated!');
}
