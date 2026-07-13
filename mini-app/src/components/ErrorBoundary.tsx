import { Component, ReactNode, ErrorInfo } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  errorMessage: string
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, errorMessage: '' }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, errorMessage: error.message }
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error('ErrorBoundary caught:', error, info)
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
          <div className="text-4xl mb-4">😕</div>
          <h2 className="text-lg font-semibold mb-2">Что-то пошло не так</h2>
          <p className="text-sm text-tg-hint mb-4">{this.state.errorMessage}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-tg-button text-tg-buttonText rounded-lg text-sm font-medium"
          >
            Перезагрузить
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
